import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ImageURLProcessor:
    """Process image URLs to use direct Zoho Creator URLs instead of downloading"""

    def __init__(self):
        # Base URL format for Zoho Creator image access
        self.base_url = "https://creatorexport.zoho.com/file/astrastaging/staging-manager/{report_name}/{record_id}/{field_name}/image-download/nRxUJtEBFywkxJJ2RNwqbbG9FTZ8QZ0wzde3u0fh5p58fbPt9Kzr06ntwR9vGeJwO63SOMJtQSMY54X3TzMvP4gqOTR14mDDnZNx?filepath=/{filename}"

    def is_image_url(self, value: str) -> bool:
        """Check if a value is a Zoho image download URL"""
        if not isinstance(value, str):
            return False

        # Pattern for Zoho image download URLs
        pattern = r'/api/v2/.+/report/.+/\d+/.+/download\?filepath=.+\.(png|jpg|jpeg|gif|webp|bmp)'
        return bool(re.search(pattern, value, re.IGNORECASE))

    def extract_image_info(self, url: str) -> Dict[str, str]:
        """Extract report name, field name, record ID and filename from image URL"""
        # Example: /api/v2/astrastaging/staging-manager/report/Item_Report/3692314000020628019/Item_Image/download?filepath=1746843200617_81CjhHJIGCL._AC_SL1500_.png

        match = re.search(r'/report/([^/]+)/(\d+)/([^/]+)/download\?filepath=(.+)', url)
        if match:
            return {
                'report_name': match.group(1),
                'record_id': match.group(2),
                'field_name': match.group(3),
                'filename': match.group(4)
            }
        return {}

    def generate_creator_url(self, report_name: str, record_id: str, field_name: str, filename: str) -> str:
        """Generate direct Zoho Creator URL for an image"""
        return self.base_url.format(
            report_name=report_name,
            record_id=record_id,
            field_name=field_name,
            filename=filename
        )

    def process_records_for_urls(self, records: List[Dict], report_name: str) -> Tuple[List[Dict], int]:
        """Process records to replace image URLs with Zoho Creator URLs

        Args:
            records: List of records from Zoho
            report_name: Name of the report

        Returns:
            Tuple of (updated_records, urls_processed_count)
        """
        updated_records: List[Dict] = []
        urls_processed = 0

        for record in records:
            updated_record = record.copy()
            record_id = str(record.get('ID', ''))

            if not record_id:
                logger.warning(f"Record missing ID, skipping URL processing")
                updated_records.append(updated_record)
                continue

            # Check each field for image URLs
            for field_name, value in record.items():
                if self.is_image_url(value):
                    # Extract image info from original URL
                    info = self.extract_image_info(value)
                    if not info or not info.get('filename'):
                        logger.warning(f"Could not extract image info from URL: {value}")
                        continue

                    filename = info['filename']

                    # Generate Zoho Creator URL
                    creator_url = self.generate_creator_url(
                        report_name,
                        record_id,
                        field_name,
                        filename
                    )

                    # Update the record with the new URL
                    updated_record[field_name] = creator_url
                    updated_record[f"{field_name}_original_api_url"] = value
                    urls_processed += 1

                    logger.debug(f"Processed URL for {field_name} in record {record_id}: {filename}")

            updated_records.append(updated_record)

        if urls_processed > 0:
            logger.info(f"Processed {urls_processed} image URLs for {len(records)} records")

        return updated_records, urls_processed

# Global instance
image_url_processor = ImageURLProcessor()
