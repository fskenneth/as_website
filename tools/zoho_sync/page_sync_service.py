"""
Page Sync Service - Polls Zoho report and syncs to local database.
Uses web scraping with Playwright for change detection, with targeted
API calls only when image URLs need resolution (files.zohopublic.com URLs).
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List
from .page_scraper import ZohoPageScraper, REPORT_URL
from .database import db
from .zoho_api import zoho_api
from .image_url_processor import image_url_processor
from .utils import get_toronto_now

logger = logging.getLogger(__name__)


class PageSyncService:
    """
    Polls Zoho report page and syncs modified items to local database.
    """

    def __init__(self, poll_interval_seconds: int = 30):
        self.poll_interval = poll_interval_seconds
        self.scraper = None
        self.is_running = False
        self.last_sync_time = None
        self.sync_count = 0
        self.error_count = 0

    async def initialize(self):
        """Initialize the scraper"""
        self.scraper = ZohoPageScraper()
        await self.scraper.initialize()
        logger.info(f"PageSyncService initialized with {self.poll_interval}s polling interval")

    async def close(self):
        """Cleanup resources"""
        self.is_running = False
        if self.scraper:
            await self.scraper.close()
        logger.info("PageSyncService closed")

    async def sync_once(self) -> Dict:
        """
        Perform a single sync operation.
        Returns dict with sync results.
        """
        start_time = get_toronto_now()
        result = {
            "timestamp": start_time.isoformat(),
            "status": "success",
            "records_found": 0,
            "records_synced": 0,
            "errors": []
        }

        try:
            # Fetch modified items from report
            items = await self.scraper.fetch_and_parse()
            result["records_found"] = len(items)

            if not items:
                logger.debug("No modified items found")
                return result

            logger.info(f"Found {len(items)} modified items to sync")

            # Ensure database is connected
            if not db._connection:
                await db.connect()

            # Upsert each item to the database (only if Modified_Time is newer)
            table_name = "Item_Report"
            synced = 0
            skipped = 0

            for item in items:
                try:
                    item_id = item.get('ID')
                    new_modified_time = item.get('Modified_Time')

                    # Extract API resolution metadata before upserting
                    image_fields_need_api = item.pop('_image_fields_need_api', [])

                    # Check if record exists and compare Modified_Time
                    existing = await db.fetchone(
                        f"SELECT Modified_Time, Item_Image, Resized_Image FROM Item_Report WHERE ID = ?",
                        (item_id,)
                    )

                    if existing and existing.get('Modified_Time') == new_modified_time:
                        # Record hasn't changed, skip
                        skipped += 1
                        logger.debug(f"Skipped unchanged item {item_id}")
                        continue

                    # Preserve local Model_3D - don't overwrite with empty value from scraper
                    if not item.get('Model_3D'):
                        item.pop('Model_3D', None)

                    # Upsert the record (new or modified)
                    upsert_result = await db.upsert_records(table_name, [item])
                    if upsert_result["successful"] > 0:
                        synced += 1
                        logger.info(f"Synced item {item_id}: {item.get('Item_Name')}")

                        # Resolve image URLs via API if needed.
                        # Always resolve when record was modified and had files.zohopublic.com URLs,
                        # since the image itself may have been updated.
                        if image_fields_need_api:
                            await self._resolve_image_urls(item_id, image_fields_need_api)

                except Exception as e:
                    error_msg = f"Error syncing item {item.get('ID')}: {e}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)

            if skipped > 0:
                logger.info(f"Skipped {skipped} unchanged items")

            result["records_synced"] = synced
            self.sync_count += synced
            self.last_sync_time = get_toronto_now()

            # Log sync to database
            await db.log_sync("page_scrape", table_name, "success", synced)

            duration = (get_toronto_now() - start_time).total_seconds()
            logger.info(f"Sync completed: {synced}/{len(items)} items in {duration:.2f}s")

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            self.error_count += 1
            logger.error(f"Sync error: {e}")

        return result

    async def _resolve_image_urls(self, record_id: str, fields: List[str]):
        """Fetch correct image URLs from Zoho API for fields that had files.zohopublic.com URLs"""
        try:
            api_record = await zoho_api.get_record_by_id('Item_Report', record_id)
            if not api_record:
                logger.warning(f"Could not fetch record {record_id} from API for image URL resolution")
                return

            for field in fields:
                api_url = api_record.get(field)
                if not api_url or not isinstance(api_url, str):
                    continue

                # API returns URLs like /api/v2/.../download?filepath=ACTUAL_FILENAME
                if '/api/v2/' in api_url:
                    info = image_url_processor.extract_image_info(api_url)
                    if info and info.get('filename'):
                        creator_url = image_url_processor.generate_creator_url(
                            'Item_Report', record_id, field, info['filename']
                        )
                        await db.execute(
                            f"UPDATE Item_Report SET {field} = ? WHERE ID = ?",
                            (creator_url, record_id)
                        )
                        logger.info(f"Resolved {field} URL for record {record_id} via API: {info['filename']}")
        except Exception as e:
            logger.error(f"Failed to resolve image URLs for record {record_id}: {e}")

    async def start_polling(self):
        """
        Start the polling loop.
        Runs continuously until stopped.
        """
        if not self.scraper:
            await self.initialize()

        self.is_running = True
        logger.info(f"Starting polling loop (interval: {self.poll_interval}s)")

        while self.is_running:
            try:
                result = await self.sync_once()

                if result["records_found"] > 0:
                    logger.info(f"Poll result: {result['records_synced']} synced, {len(result['errors'])} errors")

            except Exception as e:
                logger.error(f"Polling error: {e}")
                self.error_count += 1

            # Wait for next poll
            await asyncio.sleep(self.poll_interval)

    def stop_polling(self):
        """Stop the polling loop"""
        self.is_running = False
        logger.info("Polling stopped")

    def get_status(self) -> Dict:
        """Get current service status"""
        return {
            "is_running": self.is_running,
            "poll_interval_seconds": self.poll_interval,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "total_synced": self.sync_count,
            "error_count": self.error_count,
            "report_url": REPORT_URL
        }


# Global service instance
_sync_service = None


def get_sync_service(poll_interval: int = 30) -> PageSyncService:
    """Get or create the sync service singleton"""
    global _sync_service
    if _sync_service is None:
        _sync_service = PageSyncService(poll_interval)
    return _sync_service


async def start_background_sync(poll_interval: int = 30):
    """
    Start background sync as an async task.
    Returns the task for management.
    """
    service = get_sync_service(poll_interval)
    await service.initialize()
    task = asyncio.create_task(service.start_polling())
    return task


async def stop_background_sync():
    """Stop the background sync"""
    global _sync_service
    if _sync_service:
        _sync_service.stop_polling()
        await _sync_service.close()
        _sync_service = None


# CLI test
async def test_sync():
    """Test single sync operation"""
    print("Testing Page Sync Service...")
    print(f"Report URL: {REPORT_URL}")

    service = PageSyncService()
    await service.initialize()

    try:
        result = await service.sync_once()
        print(f"\nSync Result:")
        print(f"  Status: {result['status']}")
        print(f"  Records found: {result['records_found']}")
        print(f"  Records synced: {result['records_synced']}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(test_sync())
