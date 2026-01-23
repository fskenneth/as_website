"""
Zoho Report Page Scraper - Uses Playwright to scrape Item_Report_Sync
Polls the public report permalink and extracts recently modified items.
0 API calls - pure web scraping approach.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Handle both relative and absolute imports
try:
    from .image_url_processor import image_url_processor
except ImportError:
    from image_url_processor import image_url_processor

logger = logging.getLogger(__name__)

# Report URL - filtered to show items modified in last 1 minute
REPORT_URL = "https://creatorapp.zohopublic.com/astrastaging/staging-manager/report-perma/Item_Report_Sync/CunRbYdQssjbDhfPZAwntBJEJ5v5pS57aa5CA5exMjmg9KWEDPDUOYxWaUNuYHSFEZQysbZaf5qVXpWSHEDRg3mYazB50OFAjBXx"


class ZohoPageScraper:
    """Scrapes Zoho Creator report using Playwright"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize Playwright browser"""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        logger.info("Playwright browser initialized")

    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright browser closed")

    async def fetch_modified_items(self) -> List[Dict]:
        """
        Fetch recently modified items from the Zoho report.
        Returns list of item dictionaries.
        """
        if not self.page:
            await self.initialize()

        try:
            logger.info(f"Navigating to report: {REPORT_URL}")
            await self.page.goto(REPORT_URL, wait_until="networkidle", timeout=30000)

            # Wait for table to load or "No records" message
            await asyncio.sleep(2)

            # Check if there are no records
            no_records = await self.page.query_selector('text="No records match your specified criteria!"')
            if no_records:
                logger.info("No modified records found")
                return []

            # Wait for table rows to appear
            await self.page.wait_for_selector('tbody tr', timeout=10000)

            # Extract data using JavaScript
            data = await self.page.evaluate('''() => {
                const results = [];

                // Get all header cells (th elements or specific header divs)
                const headerRow = document.querySelector('thead tr, .zc_header_row');
                let headers = [];

                if (headerRow) {
                    headers = Array.from(headerRow.querySelectorAll('th, td')).map(h => h.textContent.trim());
                }

                // Fallback: Look for column header elements
                if (headers.length === 0) {
                    const headerDivs = document.querySelectorAll('[class*="header"] [class*="cell"], th');
                    headers = Array.from(headerDivs).map(h => h.textContent.trim()).filter(h => h);
                }

                // Get all data rows
                const rows = document.querySelectorAll('tbody tr');

                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length === 0) return;

                    const rowData = {};

                    // Extract text from each cell
                    cells.forEach((cell, idx) => {
                        let value = cell.textContent.trim();

                        // Check for images
                        const img = cell.querySelector('img');
                        if (img) {
                            // Try to extract original URL from various sources
                            // 1. Check data-src attribute (often contains original URL)
                            if (img.dataset.src && img.dataset.src.includes('files.zohopublic.com')) {
                                value = img.dataset.src;
                            }
                            // 2. Check if src contains files.zohopublic.com
                            else if (img.src && img.src.includes('files.zohopublic.com')) {
                                value = img.src;
                            }
                            // 3. Try to extract from imgproxy URL
                            else if (img.src && img.src.includes('imgproxy')) {
                                // Extract the original URL from imgproxy URL pattern
                                // Format: /imgproxy/.../.../aHR0cHM6Ly9maWxlcy56b2hvcHVibGljLmNvbS8uLi4
                                const match = img.src.match(/\\/([^\\/]+)$/);
                                if (match) {
                                    try {
                                        const decoded = atob(match[1].replace(/-/g, '+').replace(/_/g, '/'));
                                        if (decoded.startsWith('http')) {
                                            value = decoded;
                                        } else {
                                            value = img.src;
                                        }
                                    } catch (e) {
                                        value = img.src;
                                    }
                                } else {
                                    value = img.src;
                                }
                            }
                            // 4. Fallback to whatever src is available
                            else if (img.src) {
                                value = img.src;
                            }
                        }

                        // Use header name if available, otherwise use index
                        const key = headers[idx] || `col_${idx}`;
                        rowData[key] = value;
                    });

                    // Only add if we have an ID
                    if (rowData['ID'] || rowData['col_0']) {
                        results.push(rowData);
                    }
                });

                return {
                    headers: headers,
                    rowCount: results.length,
                    data: results
                };
            }''')

            logger.info(f"Extracted {data['rowCount']} records from report")
            return data['data']

        except Exception as e:
            logger.error(f"Error fetching modified items: {e}")
            return []

    async def fetch_and_parse(self) -> List[Dict]:
        """
        Fetch and parse items, normalizing field names for database.
        """
        raw_items = await self.fetch_modified_items()

        parsed_items = []
        for item in raw_items:
            parsed = self._normalize_item(item)
            if parsed:
                parsed_items.append(parsed)

        return parsed_items

    def _normalize_item(self, raw_item: Dict) -> Optional[Dict]:
        """
        Normalize raw scraped item to match database schema.
        Maps scraped column names to database field names.
        Transforms files.zohopublic.com URLs to creatorexport.zoho.com URLs.
        """
        # Field mapping from scraped names to database names
        field_map = {
            'ID': 'ID',
            'col_0': 'ID',  # Fallback
            'Added Time': 'Added_Time',
            'Added User': 'Added_User',
            'Modified Time': 'Modified_Time',
            'Modified User': 'Modified_User',
            'Item Index': 'Item_Index',
            'Item Type': 'Item_Type',
            'Item Name': 'Item_Name',
            'Item Notes': 'Item_Notes',
            'Matching Item Name': 'Matching_Item_Name',
            'Item Width (Inch) 宽': 'Item_Width',
            'Item Height (Inch) 高': 'Item_Height',
            'Item Depth (Inch) 厚': 'Item_Depth',
            'Item Size': 'Item_Size',
            'Item Style': 'Item_Style',
            'Item Color': 'Item_Color',
            'Item Tone': 'Item_Tone',
            'Item Material': 'Item_Material',
            '3D Model': 'Model_3D',
            'Item Image': 'Item_Image',
            'Resized Image': 'Resized_Image',
            'QR Code 二维码': 'QR_Code',
            'Rack': 'Rack',
            'Duplicate Number': 'Duplicate_Number',
            'Same As Item': 'Same_As_Item',
            'Current Location': 'Current_Location',
            'Item Count in Warehouse': 'Item_Count_in_Warehouse',
            'Last Update Date': 'Last_Update_Date',
            'Last Moved By': 'Last_Moved_By',
            'Move Count': 'Move_Count',
            'Rentable': 'Rentable',
            'Last Manually Scan Time': 'Last_Manually_Scan_Time',
            'Last Manually Scanned By': 'Last_Manually_Scanned_By',
            'Dock': 'Dock',
        }

        normalized = {}
        for scraped_name, db_name in field_map.items():
            if scraped_name in raw_item:
                value = raw_item[scraped_name]
                # Clean up empty strings
                if value == '' or value == 'null':
                    value = None
                normalized[db_name] = value

        # Must have ID
        if not normalized.get('ID'):
            return None

        # Transform files.zohopublic.com URLs to creatorexport.zoho.com format
        report_name = "Item_Report"

        # Transform Item_Image if present
        if normalized.get('Item_Image') and 'files.zohopublic.com' in normalized['Item_Image']:
            result = image_url_processor.transform_files_zohopublic_url(
                normalized['Item_Image'],
                'Item_Image',
                report_name
            )
            if result['success']:
                normalized['Item_Image'] = result['url']
                logger.debug(f"Transformed Item_Image URL for record {normalized['ID']}")

        # Transform Resized_Image if present
        if normalized.get('Resized_Image') and 'files.zohopublic.com' in normalized['Resized_Image']:
            result = image_url_processor.transform_files_zohopublic_url(
                normalized['Resized_Image'],
                'Resized_Image',
                report_name
            )
            if result['success']:
                normalized['Resized_Image'] = result['url']
                logger.debug(f"Transformed Resized_Image URL for record {normalized['ID']}")

        return normalized


# Singleton instance
_scraper = None

async def get_scraper() -> ZohoPageScraper:
    """Get or create scraper instance"""
    global _scraper
    if _scraper is None:
        _scraper = ZohoPageScraper()
        await _scraper.initialize()
    return _scraper


async def scrape_modified_items() -> List[Dict]:
    """
    Main entry point - scrape and return modified items.
    """
    scraper = await get_scraper()
    return await scraper.fetch_and_parse()


# Test function
async def test_scraper():
    """Test the scraper"""
    print("Testing Zoho Page Scraper...")
    print(f"Report URL: {REPORT_URL}")

    scraper = ZohoPageScraper()
    await scraper.initialize()

    try:
        items = await scraper.fetch_and_parse()
        print(f"\nFound {len(items)} modified items:")
        for item in items:
            print(f"  - ID: {item.get('ID')}, Name: {item.get('Item_Name')}, Modified: {item.get('Modified_Time')}")

        if items:
            print(f"\nFull first item:")
            print(json.dumps(items[0], indent=2, default=str))
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_scraper())
