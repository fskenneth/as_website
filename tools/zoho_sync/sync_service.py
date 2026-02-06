import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .database import db
from .zoho_api import zoho_api
from .image_downloader import image_downloader
from .image_url_processor import image_url_processor
from .utils import get_toronto_now, get_toronto_now_iso
import logging

logger = logging.getLogger(__name__)

class SyncService:
    def _preserve_model_3d(self, records: List[Dict], existing_records: Dict[str, Dict]) -> List[Dict]:
        """Preserve locally-set Model_3D values when Zoho sends empty values.
        Also maps Zoho field name '3D_Model' to local column 'Model_3D'."""
        preserved = []
        preserved_count = 0
        for record in records:
            updated = record.copy()
            record_id = str(record.get('ID', ''))
            existing = existing_records.get(record_id) if existing_records else None

            # Map Zoho API field name to local DB column name
            for key in ('3D_Model', '3D Model'):
                if key in updated:
                    val = updated.pop(key)
                    if val and 'Model_3D' not in updated:
                        updated['Model_3D'] = val

            # Preserve local Model_3D if incoming is empty but local has value
            if existing:
                existing_model = existing.get('Model_3D')
                incoming_model = updated.get('Model_3D')
                if existing_model and not incoming_model:
                    updated['Model_3D'] = existing_model
                    preserved_count += 1

            preserved.append(updated)

        if preserved_count > 0:
            logger.info(f"Preserved {preserved_count} local Model_3D values during sync")
        return preserved

    async def sync_report(self, report_name: str, sync_type: str = "daily") -> Dict:
        """Sync a single report from Zoho Creator"""
        start_time = get_toronto_now()
        synced_count = 0

        try:
            logger.info(f"Starting {sync_type} sync for {report_name}")

            # Prepare table name
            table_name = db._sanitize_name(report_name)

            # Check if table exists, create if needed
            if not await db.table_exists(table_name):
                logger.info(f"Table {table_name} doesn't exist, creating from API metadata...")
                metadata = await zoho_api.get_report_metadata(report_name)
                if metadata and metadata["fields"]:
                    await db.create_table_from_fields(table_name, metadata["fields"])
                    logger.info(f"Created table {table_name} with {len(metadata['fields'])} fields")
                else:
                    raise Exception(f"Could not fetch metadata for {report_name}")

            # Get total count for verification (especially for full sync)
            expected_total_count = None
            if sync_type == "full":
                logger.info(f"Getting total record count for {report_name}...")
                expected_total_count = await zoho_api.get_report_total_count(report_name)
                logger.info(f"Total records in Zoho for {report_name}: {expected_total_count}")

            # Get records based on sync type
            if sync_type == "daily":
                records = await zoho_api.get_today_modified_records(report_name)
            elif sync_type == "full":
                records = await zoho_api.get_all_report_data(report_name)
            else:
                # For incremental sync, get last sync time
                sync_meta = await db.get_sync_metadata(table_name)
                if sync_meta and sync_meta["last_modified_time"]:
                    last_sync = datetime.fromisoformat(sync_meta["last_modified_time"])
                    records = await zoho_api.get_modified_records_since(report_name, last_sync)
                else:
                    # First sync, get all records
                    records = await zoho_api.get_all_report_data(report_name)

            if not records:
                logger.info(f"No modified records found for {report_name}")
                await db.log_sync(sync_type, table_name, "success", 0)
                return {
                    "report_name": report_name,
                    "status": "success",
                    "records_synced": 0,
                    "message": "No records to sync"
                }

            # Get existing records for image comparison
            existing_records = {}
            try:
                # Get existing records from database
                existing_data = await db.get_all_records(table_name)
                existing_records = {str(r.get('ID', '')): r for r in existing_data}
            except Exception as e:
                logger.warning(f"Could not fetch existing records for comparison: {e}")

            # Process image URLs to use Zoho Creator URLs
            urls_processed = 0
            logger.info(f"Processing image URLs for {len(records)} records in {report_name}")
            records_with_urls, urls_processed = image_url_processor.process_records_for_urls(
                records,
                report_name,
                existing_records  # Pass existing records to preserve good URLs
            )

            # Preserve local Model_3D values
            records_with_urls = self._preserve_model_3d(records_with_urls, existing_records)

            # Verify record count for full sync
            if sync_type == "full" and expected_total_count:
                if len(records) != expected_total_count:
                    logger.warning(f"⚠️  Record count mismatch! Expected {expected_total_count} records from Zoho, but fetched {len(records)}")
                else:
                    logger.info(f"✓ Pre-sync verification passed: {len(records)} records match expected count")

            # Save local Model_3D values before clearing for full sync
            saved_model_3d = {}
            if sync_type == "full":
                for rid, rec in existing_records.items():
                    model_val = rec.get('Model_3D')
                    if model_val:
                        saved_model_3d[rid] = model_val
                if saved_model_3d:
                    logger.info(f"Saved {len(saved_model_3d)} Model_3D values before full sync clear")
                await db.clear_table(table_name)

            # Upsert records with Zoho Creator URLs
            upsert_result = await db.upsert_records(table_name, records_with_urls)

            # Restore Model_3D values after full sync
            if saved_model_3d:
                restored = 0
                for rid, model_val in saved_model_3d.items():
                    await db.execute(
                        f"UPDATE {table_name} SET Model_3D = ? WHERE ID = ? AND (Model_3D IS NULL OR Model_3D = '')",
                        (model_val, rid)
                    )
                    restored += 1
                logger.info(f"Restored {restored} Model_3D values after full sync")
            synced_count = upsert_result["successful"]
            skipped_count = upsert_result["skipped"]

            # Log warning if any records were skipped
            if skipped_count > 0:
                logger.warning(f"⚠️  {skipped_count} records were skipped during sync for {report_name} (missing ID field)")

            # Update sync metadata with actual successful count
            last_modified = max(
                (r.get("Modified_Time", "") for r in records if r.get("Modified_Time")),
                default=""
            )

            if last_modified:
                await db.update_sync_metadata(table_name, last_modified, synced_count)

            await db.log_sync(sync_type, table_name, "success", synced_count)

            # Perform post-sync verification
            verification = await db.verify_sync_counts(table_name)
            if verification["mismatch"]:
                logger.warning(f"Post-sync verification found count mismatch for {table_name}: " +
                             f"expected {synced_count}, actual {verification['actual_count']}")

            # Final verification for full sync
            if sync_type == "full":
                # Count actual records in database
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                result = await db.fetchone(count_query)
                actual_count = result['count'] if result else 0

                # Special checks for Item_Report
                if report_name == "Item_Report":
                    # Count images
                    item_image_query = f"SELECT COUNT(*) as count FROM {table_name} WHERE Item_Image IS NOT NULL"
                    resized_image_query = f"SELECT COUNT(*) as count FROM {table_name} WHERE Resized_Image IS NOT NULL"

                    item_result = await db.fetchone(item_image_query)
                    resized_result = await db.fetchone(resized_image_query)

                    item_image_count = item_result['count'] if item_result else 0
                    resized_image_count = resized_result['count'] if resized_result else 0

                    logger.info(f"=== {report_name} Full Sync Verification ===")
                    logger.info(f"Expected records (from Zoho): {expected_total_count}")
                    logger.info(f"Actual records in DB: {actual_count}")
                    logger.info(f"Records with Item_Image: {item_image_count}")
                    logger.info(f"Records with Resized_Image: {resized_image_count}")
                else:
                    logger.info(f"=== {report_name} Full Sync Verification ===")
                    logger.info(f"Expected records (from Zoho): {expected_total_count}")
                    logger.info(f"Actual records in DB: {actual_count}")

                if expected_total_count and actual_count != expected_total_count:
                    logger.warning(f"⚠️  Final record count mismatch! Expected {expected_total_count}, got {actual_count}")
                    logger.warning(f"Missing records: {expected_total_count - actual_count}")
                elif expected_total_count:
                    logger.info(f"✅ Final verification passed: {actual_count} records successfully synced")

            duration = (get_toronto_now() - start_time).total_seconds()
            logger.info(f"Synced {synced_count} records for {report_name} in {duration:.2f}s")

            # Build message with skipped records info
            message = f"Successfully synced {synced_count} records and processed {urls_processed} image URLs"
            if skipped_count > 0:
                message += f" (⚠️ {skipped_count} records skipped - missing ID field)"

            return {
                "report_name": report_name,
                "status": "success",
                "records_synced": synced_count,
                "records_skipped": skipped_count,
                "urls_processed": urls_processed,
                "duration": duration,
                "message": message,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to sync {report_name}: {error_msg}")
            await db.log_sync(sync_type, table_name, "failed", synced_count, error_msg)

            return {
                "report_name": report_name,
                "status": "failed",
                "records_synced": synced_count,
                "error": error_msg,
                "message": f"Sync failed: {error_msg}"
            }

    async def sync_reports(self, report_names: List[str], sync_type: str = "daily") -> Dict:
        """Sync multiple reports"""
        results = []

        for report_name in report_names:
            result = await self.sync_report(report_name, sync_type)
            results.append(result)

        # Summary
        total_synced = sum(r["records_synced"] for r in results if r["status"] == "success")
        total_urls = sum(r.get("urls_processed", 0) for r in results if r["status"] == "success")
        failed_reports = [r["report_name"] for r in results if r["status"] == "failed"]

        return {
            "status": "success" if not failed_reports else "partial",
            "total_records_synced": total_synced,
            "total_urls_processed": total_urls,
            "results": results,
            "failed_reports": failed_reports,
            "message": f"Synced {total_synced} records across {len(report_names)} reports and processed {total_urls} image URLs",
        }

    async def get_available_reports(self) -> List[str]:
        """Get list of available reports from Zoho API"""
        try:
            # Fetch all reports from Zoho API
            reports = await zoho_api.list_all_reports()

            # Extract report link names (used for API calls)
            report_names = [report["link_name"] for report in reports]

            logger.info(f"Found {len(report_names)} reports from Zoho API")
            return sorted(report_names)
        except Exception as e:
            logger.error(f"Failed to fetch reports from API, falling back to defaults: {e}")
            # Fallback to known reports if API fails
            return ["Item_Report", "All_Quotes"]

    async def get_available_reports_with_display_names(self) -> List[Dict]:
        """Get list of available reports with display names from Zoho API"""
        try:
            # Fetch all reports from Zoho API
            reports = await zoho_api.list_all_reports()

            # Return sorted list of report info
            return sorted(reports, key=lambda x: x["display_name"])
        except Exception as e:
            logger.error(f"Failed to fetch reports from API, falling back to defaults: {e}")
            # Fallback to known reports if API fails
            return [
                {"link_name": "Item_Report", "display_name": "Item Report"},
                {"link_name": "All_Quotes", "display_name": "All Quotes"}
            ]

    async def get_sync_status(self) -> Dict:
        """Get sync status for all reports"""
        stats = await db.get_table_stats()
        history = await db.get_sync_history(limit=10)

        # Format stats
        report_status = {}
        for stat in stats:
            report_status[stat["table_name"]] = {
                "last_modified": stat["last_modified_time"],
                "record_count": stat["record_count"],
                "last_sync": stat["updated_at"],
                "successful_syncs": stat["successful_syncs"],
                "failed_syncs": stat["failed_syncs"]
            }

        return {
            "reports": report_status,
            "recent_syncs": history
        }

    async def smart_incremental_sync(self, report_name: str) -> Dict:
        """
        Smart incremental sync - only fetches records modified since last check.
        Used for background sync to keep local DB updated without full syncs.
        """
        start_time = get_toronto_now()
        table_name = db._sanitize_name(report_name)

        try:
            # Get last sync metadata
            metadata = await db.get_sync_metadata(table_name)

            if not metadata or not metadata.get('last_modified_time'):
                # No metadata, need full sync
                logger.info(f"No sync metadata for {report_name}, running full sync")
                return await self.sync_report(report_name, "full")

            last_modified = metadata['last_modified_time']
            logger.info(f"Smart sync for {report_name} - checking records since {last_modified}")

            # Parse last modified time
            try:
                # Handle various date formats from Zoho
                if 'T' in last_modified:
                    last_sync_dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                else:
                    # Try parsing Zoho format: "31-Dec-2025 09:04:40"
                    last_sync_dt = datetime.strptime(last_modified, "%d-%b-%Y %H:%M:%S")
            except ValueError:
                logger.warning(f"Could not parse last_modified_time: {last_modified}, running daily sync")
                return await self.sync_report(report_name, "daily")

            # Fetch records modified since last sync
            records = await zoho_api.get_modified_records_since(report_name, last_sync_dt)

            if not records:
                logger.info(f"No modified records found for {report_name} since {last_modified}")
                return {
                    "report_name": report_name,
                    "status": "success",
                    "records_synced": 0,
                    "message": "No new changes"
                }

            logger.info(f"Found {len(records)} modified records for {report_name}")

            # Get existing records to preserve good URLs
            existing_records = {}
            try:
                existing_data = await db.get_all_records(table_name)
                existing_records = {str(r.get('ID', '')): r for r in existing_data}
            except Exception as e:
                logger.warning(f"Could not fetch existing records for comparison: {e}")

            # Process image URLs
            records_with_urls, urls_processed = image_url_processor.process_records_for_urls(
                records, report_name, existing_records
            )

            # Preserve local Model_3D values
            records_with_urls = self._preserve_model_3d(records_with_urls, existing_records)

            # Upsert records (not clearing table - incremental update)
            upsert_result = await db.upsert_records(table_name, records_with_urls)
            synced_count = upsert_result["successful"]

            # Update sync metadata
            new_last_modified = max(
                (r.get("Modified_Time", "") for r in records if r.get("Modified_Time")),
                default=last_modified
            )

            if new_last_modified:
                # Get current record count
                count_result = await db.fetchone(f"SELECT COUNT(*) as count FROM {table_name}")
                record_count = count_result['count'] if count_result else 0
                await db.update_sync_metadata(table_name, new_last_modified, record_count)

            await db.log_sync("incremental", table_name, "success", synced_count)

            duration = (get_toronto_now() - start_time).total_seconds()
            logger.info(f"Smart sync completed: {synced_count} records in {duration:.2f}s")

            return {
                "report_name": report_name,
                "status": "success",
                "records_synced": synced_count,
                "urls_processed": urls_processed,
                "duration": duration,
                "message": f"Synced {synced_count} modified records"
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Smart sync failed for {report_name}: {error_msg}")
            await db.log_sync("incremental", table_name, "failed", 0, error_msg)

            return {
                "report_name": report_name,
                "status": "failed",
                "records_synced": 0,
                "error": error_msg
            }

    async def smart_sync_check(self) -> Dict:
        """
        Smart sync that only uses API credits when changes are detected.
        1. Fetch Item_Report_Sync (today's modified records - lightweight)
        2. Compare with local database
        3. Only sync records that have actually changed
        """
        start_time = get_toronto_now()

        try:
            # Step 1: Get today's modified records from Item_Report_Sync
            sync_records = await zoho_api.get_sync_report_records()

            if not sync_records:
                logger.info("[Smart Sync] No modified records found today")
                return {
                    "status": "success",
                    "changes_detected": False,
                    "records_synced": 0,
                    "message": "No modified records today"
                }

            # Step 2: Compare with local database to find actual changes
            table_name = "Item_Report"
            records_to_sync = []

            for record in sync_records:
                record_id = record.get("ID")
                if not record_id:
                    continue

                # Get local record
                local_record = await db.fetchone(
                    f"SELECT * FROM {table_name} WHERE ID = ?",
                    (record_id,)
                )

                if not local_record:
                    # New record, needs sync
                    records_to_sync.append(record)
                    logger.info(f"[Smart Sync] New record detected: {record_id}")
                else:
                    # Compare key fields to detect changes
                    # Check if any important field has changed
                    changed = False
                    compare_fields = ['Item_Depth', 'Item_Width', 'Item_Height', 'Item_Name',
                                     'Current_Location', 'Item_Notes', 'Last_Update_Date']

                    for field in compare_fields:
                        zoho_value = record.get(field)
                        local_value = local_record.get(field) if local_record else None

                        # Handle Current_Location which might be a dict in Zoho
                        if field == 'Current_Location':
                            if isinstance(zoho_value, dict):
                                zoho_value = zoho_value.get('display_value', '')
                            # Local value might be stored as JSON string
                            if isinstance(local_value, str) and local_value.startswith('{'):
                                try:
                                    local_dict = json.loads(local_value.replace("'", '"'))
                                    local_value = local_dict.get('display_value', local_value)
                                except:
                                    pass

                        # Convert to string for comparison
                        zoho_str = str(zoho_value) if zoho_value is not None else ""
                        local_str = str(local_value) if local_value is not None else ""

                        if zoho_str != local_str:
                            changed = True
                            logger.info(f"[Smart Sync] Change detected in {record_id}: {field} changed from '{local_str}' to '{zoho_str}'")
                            break

                    if changed:
                        records_to_sync.append(record)

            if not records_to_sync:
                logger.info("[Smart Sync] No actual changes detected")
                return {
                    "status": "success",
                    "changes_detected": False,
                    "records_synced": 0,
                    "message": "No changes detected (local DB is up to date)"
                }

            # Step 3: Sync only the changed records
            logger.info(f"[Smart Sync] Syncing {len(records_to_sync)} changed records")

            # Get existing records to preserve good URLs
            existing_records = {}
            try:
                existing_data = await db.get_all_records(table_name)
                existing_records = {str(r.get('ID', '')): r for r in existing_data}
            except Exception as e:
                logger.warning(f"Could not fetch existing records for comparison: {e}")

            # Process image URLs
            records_with_urls, urls_processed = image_url_processor.process_records_for_urls(
                records_to_sync, "Item_Report", existing_records
            )

            # Preserve local Model_3D values
            records_with_urls = self._preserve_model_3d(records_with_urls, existing_records)

            # Upsert only the changed records
            upsert_result = await db.upsert_records(table_name, records_with_urls)
            synced_count = upsert_result["successful"]

            # Log the sync
            await db.log_sync("smart", table_name, "success", synced_count)

            duration = (get_toronto_now() - start_time).total_seconds()
            logger.info(f"[Smart Sync] Completed: {synced_count} records in {duration:.2f}s")

            return {
                "status": "success",
                "changes_detected": True,
                "records_synced": synced_count,
                "urls_processed": urls_processed,
                "duration": duration,
                "message": f"Synced {synced_count} changed records"
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[Smart Sync] Error: {error_msg}")
            return {
                "status": "failed",
                "changes_detected": False,
                "records_synced": 0,
                "error": error_msg
            }

# Service instance
sync_service = SyncService()
