import aiosqlite
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .config import settings
from .utils import get_toronto_now_iso
import logging
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: Path = settings.database_path):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
        # Create directories if they don't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """Establish database connection"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self.init_core_tables()

    async def disconnect(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()

    async def init_core_tables(self):
        """Initialize core database tables"""
        async with self._connection.cursor() as cursor:
            # Sync metadata table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    table_name TEXT PRIMARY KEY,
                    last_modified_time TEXT,
                    record_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sync log table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_type TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    records_synced INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sync issues table for tracking problematic records
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    record_info TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await self._connection.commit()

    async def create_table_from_fields(self, table_name: str, fields: List[str]):
        """Create a table dynamically based on field names"""
        # Sanitize table name
        safe_table_name = self._sanitize_name(table_name)

        # Build column definitions
        columns = []
        has_id_field = False
        for field in fields:
            safe_field = self._sanitize_name(field)
            if safe_field == "ID":
                has_id_field = True
                columns.append(f"{safe_field} TEXT PRIMARY KEY")
            else:
                columns.append(f"{safe_field} TEXT")

        # Add system columns
        columns.extend([
            "_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "_modified_time TEXT",
            "_sync_status TEXT DEFAULT 'active'"
        ])

        # Create table - only add ID if not already present
        if has_id_field:
            create_query = f"""
                CREATE TABLE IF NOT EXISTS {safe_table_name} (
                    {', '.join(columns)}
                )
            """
        else:
            create_query = f"""
                CREATE TABLE IF NOT EXISTS {safe_table_name} (
                    ID TEXT PRIMARY KEY,
                    {', '.join(columns)}
                )
            """

        async with self._connection.cursor() as cursor:
            await cursor.execute(create_query)

            # Create index on Modified_Time if it exists
            if "Modified_Time" in fields:
                index_query = f"""
                    CREATE INDEX IF NOT EXISTS idx_{safe_table_name}_modified
                    ON {safe_table_name} (Modified_Time)
                """
                await cursor.execute(index_query)

            await self._connection.commit()

        logger.info(f"Created table {safe_table_name} with {len(fields)} fields")

    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        safe_table_name = self._sanitize_name(table_name)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

        async with self._connection.cursor() as cursor:
            await cursor.execute(query, (safe_table_name,))
            result = await cursor.fetchone()
            return result is not None

    async def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str = "TEXT"):
        """Add a column to a table if it doesn't exist"""
        safe_table_name = self._sanitize_name(table_name)
        safe_column_name = self._sanitize_name(column_name)

        # Check if column exists
        query = f"PRAGMA table_info({safe_table_name})"
        async with self._connection.cursor() as cursor:
            await cursor.execute(query)
            columns = await cursor.fetchall()
            existing_columns = [col[1] for col in columns]

            if safe_column_name not in existing_columns:
                alter_query = f"ALTER TABLE {safe_table_name} ADD COLUMN {safe_column_name} {column_type}"
                await cursor.execute(alter_query)
                await self._connection.commit()
                logger.info(f"Added column {safe_column_name} to table {safe_table_name}")

    async def upsert_record(self, table_name: str, record: Dict[str, Any]) -> bool:
        """Upsert a single record. Returns True if successful, False if skipped."""
        safe_table_name = self._sanitize_name(table_name)

        # Clean record keys and convert complex types to JSON
        clean_record = {}
        for key, value in record.items():
            safe_key = self._sanitize_name(key)
            # Convert dicts and lists to JSON strings
            if isinstance(value, (dict, list)):
                clean_record[safe_key] = json.dumps(value)
            else:
                clean_record[safe_key] = value

        # Add system fields
        if "Modified_Time" in clean_record:
            clean_record["_modified_time"] = clean_record["Modified_Time"]
        clean_record["_synced_at"] = get_toronto_now_iso()

        # Ensure ID field exists
        if "ID" not in clean_record:
            # Log detailed info about the skipped record
            item_info = {
                'Item_Name': clean_record.get('Item_Name', 'Unknown'),
                'Item_Barcode': clean_record.get('Item_Barcode', 'Unknown'),
                'record_keys': list(clean_record.keys())[:5]  # First 5 keys for debugging
            }
            logger.warning(f"Record missing ID field: {item_info}")

            # Log to sync_issues table
            await self.log_sync_issue(
                table_name,
                "missing_id",
                json.dumps(item_info),
                "Record skipped during sync due to missing ID field"
            )
            return False

        # Add missing columns to table
        for column_name in clean_record.keys():
            await self.add_column_if_not_exists(safe_table_name, column_name)

        # Build upsert query
        columns = list(clean_record.keys())
        placeholders = ["?" for _ in columns]
        update_pairs = [f"{col} = excluded.{col}" for col in columns if col != "ID"]

        query = f"""
            INSERT INTO {safe_table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT(ID) DO UPDATE SET
            {', '.join(update_pairs)}
        """

        values = [clean_record[col] for col in columns]

        try:
            async with self._connection.cursor() as cursor:
                await cursor.execute(query, values)
            return True
        except Exception as e:
            logger.error(f"Failed to upsert record {clean_record.get('ID', 'Unknown')}: {e}")
            return False

    async def upsert_records(self, table_name: str, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Upsert multiple records in a transaction. Returns counts of successful and skipped records."""
        successful = 0
        skipped = 0
        skipped_records = []  # Collect skipped records to log after transaction

        async with self._connection.cursor() as cursor:
            await cursor.execute("BEGIN TRANSACTION")

            try:
                for record in records:
                    # Check for ID field before processing
                    if "ID" not in record:
                        skipped += 1
                        # Collect info for logging after transaction
                        skipped_records.append({
                            'Item_Name': record.get('Item_Name', 'Unknown'),
                            'Item_Barcode': record.get('Item_Barcode', 'Unknown'),
                            'record_keys': list(record.keys())[:5]
                        })
                        continue

                    # Process record with ID
                    try:
                        # Clean and prepare record
                        clean_record = {}
                        for key, value in record.items():
                            safe_key = self._sanitize_name(key)
                            if isinstance(value, (dict, list)):
                                clean_record[safe_key] = json.dumps(value)
                            else:
                                clean_record[safe_key] = value

                        # Add system fields
                        if "Modified_Time" in clean_record:
                            clean_record["_modified_time"] = clean_record["Modified_Time"]
                        clean_record["_synced_at"] = get_toronto_now_iso()

                        # Add missing columns
                        for column_name in clean_record.keys():
                            await self.add_column_if_not_exists(table_name, column_name)

                        # Build upsert query
                        columns = list(clean_record.keys())
                        placeholders = ["?" for _ in columns]
                        update_pairs = [f"{col} = excluded.{col}" for col in columns if col != "ID"]

                        query = f"""
                            INSERT INTO {self._sanitize_name(table_name)} ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            ON CONFLICT(ID) DO UPDATE SET
                            {', '.join(update_pairs)}
                        """

                        values = [clean_record[col] for col in columns]
                        await cursor.execute(query, values)
                        successful += 1

                    except Exception as e:
                        logger.error(f"Failed to upsert record {record.get('ID', 'Unknown')}: {e}")
                        skipped += 1

                await cursor.execute("COMMIT")

                # Log skipped records after transaction completes
                for skipped_info in skipped_records:
                    logger.warning(f"Record missing ID field: {skipped_info}")
                    await self.log_sync_issue(
                        table_name,
                        "missing_id",
                        json.dumps(skipped_info),
                        "Record skipped during sync due to missing ID field"
                    )

                if skipped > 0:
                    logger.info(f"Upserted {successful} records, skipped {skipped} records for table {table_name}")

                return {"successful": successful, "skipped": skipped}
            except Exception as e:
                await cursor.execute("ROLLBACK")
                raise e

    async def clear_table(self, table_name: str):
        """Clear all records from a table"""
        safe_table_name = self._sanitize_name(table_name)
        query = f"DELETE FROM {safe_table_name}"

        async with self._connection.cursor() as cursor:
            await cursor.execute(query)
            await self._connection.commit()

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            await self._connection.commit()

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one record"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all records"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_sync_metadata(self, table_name: str, last_modified: str, record_count: int):
        """Update sync metadata for a table"""
        safe_table_name = self._sanitize_name(table_name)
        query = """
            INSERT INTO sync_metadata (table_name, last_modified_time, record_count, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(table_name) DO UPDATE SET
                last_modified_time = excluded.last_modified_time,
                record_count = excluded.record_count,
                updated_at = excluded.updated_at
        """

        now = get_toronto_now_iso()
        await self.execute(query, (safe_table_name, last_modified, record_count, now))

    async def log_sync(self, sync_type: str, table_name: str, status: str,
                      records_synced: int = 0, error_message: str = None):
        """Log sync operation"""
        query = """
            INSERT INTO sync_log (sync_type, table_name, status, records_synced, error_message)
            VALUES (?, ?, ?, ?, ?)
        """
        await self.execute(query, (sync_type, table_name, status, records_synced, error_message))

    async def log_sync_issue(self, table_name: str, issue_type: str, record_info: str, details: str = None):
        """Log a sync issue for tracking problematic records"""
        query = """
            INSERT INTO sync_issues (table_name, issue_type, record_info, details)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (table_name, issue_type, record_info, details))

    async def get_sync_metadata(self, table_name: str) -> Optional[Dict]:
        """Get sync metadata for a table"""
        safe_table_name = self._sanitize_name(table_name)
        query = "SELECT * FROM sync_metadata WHERE table_name = ?"
        return await self.fetchone(query, (safe_table_name,))

    async def get_sync_history(self, limit: int = 50) -> List[Dict]:
        """Get recent sync history"""
        query = """
            SELECT * FROM sync_log
            ORDER BY created_at DESC
            LIMIT ?
        """
        return await self.fetchall(query, (limit,))

    async def get_table_stats(self) -> List[Dict]:
        """Get statistics for all synced tables"""
        query = """
            SELECT
                sm.table_name,
                sm.last_modified_time,
                sm.record_count,
                sm.updated_at,
                (SELECT COUNT(*) FROM sync_log sl
                 WHERE sl.table_name = sm.table_name
                 AND sl.status = 'success') as successful_syncs,
                (SELECT COUNT(*) FROM sync_log sl
                 WHERE sl.table_name = sm.table_name
                 AND sl.status = 'failed') as failed_syncs
            FROM sync_metadata sm
            ORDER BY sm.table_name
        """
        return await self.fetchall(query)

    async def get_all_records(self, table_name: str) -> List[Dict]:
        """Get all records from a table"""
        safe_table_name = self._sanitize_name(table_name)

        # Check if table exists
        if not await self.table_exists(safe_table_name):
            return []

        query = f"SELECT * FROM {safe_table_name}"
        return await self.fetchall(query)

    async def verify_sync_counts(self, table_name: str) -> Dict[str, int]:
        """Verify sync counts and update metadata if needed"""
        safe_table_name = self._sanitize_name(table_name)

        # Get actual count from table
        count_query = f"SELECT COUNT(*) as count FROM {safe_table_name}"
        result = await self.fetchone(count_query)
        actual_count = result['count'] if result else 0

        # Get metadata count
        metadata = await self.get_sync_metadata(table_name)
        metadata_count = metadata['record_count'] if metadata else 0

        # If counts don't match, update metadata with actual count
        if actual_count != metadata_count:
            logger.warning(f"Count mismatch for {table_name}: metadata={metadata_count}, actual={actual_count}")
            # Update metadata with correct count
            if metadata and metadata.get('last_modified_time'):
                await self.update_sync_metadata(
                    table_name,
                    metadata['last_modified_time'],
                    actual_count
                )

        return {
            "actual_count": actual_count,
            "metadata_count": metadata_count,
            "mismatch": actual_count != metadata_count
        }

    def _sanitize_name(self, name: str) -> str:
        """Sanitize table/column names for SQLite"""
        # Replace non-alphanumeric characters with underscores
        return ''.join(c if c.isalnum() or c == '_' else '_' for c in name)

# Database instance
db = Database()
