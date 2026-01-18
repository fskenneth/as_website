"""
Zoho Write Service - Handles bidirectional sync from website to Zoho Creator
Uses a write-behind queue pattern for efficient API usage
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .database import db
from .zoho_api import zoho_api
from .utils import get_toronto_now_iso

logger = logging.getLogger(__name__)


class ZohoWriteService:
    def __init__(self):
        self.max_batch_size = 10  # Max records to sync per cycle
        self.max_retries = 3

    async def init_tables(self):
        """Initialize the pending updates table"""
        async with db._connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_zoho_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    report_name TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    new_value TEXT,
                    old_value TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    synced_at TEXT
                )
            """)

            # Create index for faster queries
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pending_status
                ON pending_zoho_updates (status, retry_count)
            """)

            # Create conflict log table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    report_name TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    local_value TEXT,
                    zoho_value TEXT,
                    resolution TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db._connection.commit()
            logger.info("Initialized pending_zoho_updates and sync_conflicts tables")

    async def queue_update(self, record_id: str, report_name: str,
                          changes: Dict[str, Any], old_values: Dict[str, Any] = None):
        """Queue record changes for sync to Zoho"""
        old_values = old_values or {}

        for field, value in changes.items():
            # Skip internal fields
            if field.startswith('_'):
                continue

            try:
                await db.execute("""
                    INSERT INTO pending_zoho_updates
                    (record_id, report_name, field_name, new_value, old_value, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record_id,
                    report_name,
                    field,
                    json.dumps(value) if not isinstance(value, str) else value,
                    json.dumps(old_values.get(field)) if old_values.get(field) and not isinstance(old_values.get(field), str) else old_values.get(field),
                    get_toronto_now_iso()
                ))
            except Exception as e:
                logger.error(f"Failed to queue update for {record_id}.{field}: {e}")

        logger.info(f"Queued {len(changes)} field updates for record {record_id}")

    async def get_pending_count(self) -> int:
        """Get count of pending updates"""
        result = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates
            WHERE status = 'pending' AND retry_count < ?
        """, (self.max_retries,))
        return result['count'] if result else 0

    async def get_pending_for_record(self, record_id: str) -> int:
        """Get count of pending updates for a specific record"""
        result = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates
            WHERE record_id = ? AND status = 'pending'
        """, (record_id,))
        return result['count'] if result else 0

    async def process_pending_updates(self) -> Dict[str, int]:
        """Process queued updates in batches"""
        processed = 0
        failed = 0

        # Get distinct records with pending updates
        pending_records = await db.fetchall("""
            SELECT DISTINCT record_id, report_name
            FROM pending_zoho_updates
            WHERE status = 'pending' AND retry_count < ?
            ORDER BY created_at ASC
            LIMIT ?
        """, (self.max_retries, self.max_batch_size))

        if not pending_records:
            return {"processed": 0, "failed": 0}

        logger.info(f"Processing {len(pending_records)} records with pending updates")

        for record in pending_records:
            success = await self._sync_record(record['record_id'], record['report_name'])
            if success:
                processed += 1
            else:
                failed += 1

        return {"processed": processed, "failed": failed}

    async def _sync_record(self, record_id: str, report_name: str) -> bool:
        """Sync a single record's pending changes to Zoho"""
        # Get all pending changes for this record
        changes = await db.fetchall("""
            SELECT id, field_name, new_value, old_value FROM pending_zoho_updates
            WHERE record_id = ? AND report_name = ? AND status = 'pending'
        """, (record_id, report_name))

        if not changes:
            return True

        # Build update payload
        data = {}
        change_ids = []
        for change in changes:
            change_ids.append(change['id'])
            value = change['new_value']
            # Try to parse JSON values
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
            data[change['field_name']] = value

        try:
            # Mark as syncing
            placeholders = ','.join(['?' for _ in change_ids])
            await db.execute(f"""
                UPDATE pending_zoho_updates SET status = 'syncing'
                WHERE id IN ({placeholders})
            """, tuple(change_ids))

            # Check for conflicts (optional - compare with current Zoho data)
            # For now, we'll do optimistic sync

            # Call Zoho Update API
            await zoho_api.update_record(report_name, record_id, data)

            # Mark as synced
            now = get_toronto_now_iso()
            await db.execute(f"""
                UPDATE pending_zoho_updates
                SET status = 'synced', synced_at = ?
                WHERE id IN ({placeholders})
            """, (now,) + tuple(change_ids))

            logger.info(f"Successfully synced {len(changes)} changes for record {record_id}")
            return True

        except Exception as e:
            # Mark as pending with retry increment
            error_msg = str(e)
            await db.execute(f"""
                UPDATE pending_zoho_updates
                SET status = 'pending',
                    retry_count = retry_count + 1,
                    error_message = ?
                WHERE id IN ({placeholders})
            """, (error_msg,) + tuple(change_ids))

            logger.error(f"Failed to sync record {record_id}: {error_msg}")
            return False

    async def get_sync_status(self) -> Dict:
        """Get write sync status summary"""
        pending = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates WHERE status = 'pending'
        """)
        syncing = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates WHERE status = 'syncing'
        """)
        synced = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates WHERE status = 'synced'
        """)
        failed = await db.fetchone("""
            SELECT COUNT(*) as count FROM pending_zoho_updates
            WHERE status = 'pending' AND retry_count >= ?
        """, (self.max_retries,))

        return {
            "pending": pending['count'] if pending else 0,
            "syncing": syncing['count'] if syncing else 0,
            "synced": synced['count'] if synced else 0,
            "failed": failed['count'] if failed else 0
        }

    async def cleanup_old_records(self, days: int = 7):
        """Clean up old synced records"""
        await db.execute("""
            DELETE FROM pending_zoho_updates
            WHERE status = 'synced'
            AND datetime(synced_at) < datetime('now', ?)
        """, (f'-{days} days',))
        logger.info(f"Cleaned up synced records older than {days} days")


# Service instance
write_service = ZohoWriteService()
