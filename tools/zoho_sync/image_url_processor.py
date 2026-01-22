import re
import base64
import json
from typing import Dict, List, Tuple
from urllib.parse import urlparse, parse_qs, unquote
import logging

logger = logging.getLogger(__name__)

class ImageURLProcessor:
    """Process image URLs to use direct Zoho Creator URLs instead of downloading"""

    def __init__(self):
        # Base URL format for Zoho Creator image access
        self.base_url = "https://creatorexport.zoho.com/file/astrastaging/staging-manager/{report_name}/{record_id}/{field_name}/image-download/nRxUJtEBFywkxJJ2RNwqbbG9FTZ8QZ0wzde3u0fh5p58fbPt9Kzr06ntwR9vGeJwO63SOMJtQSMY54X3TzMvP4gqOTR14mDDnZNx?filepath=/{filename}"

    def is_image_url(self, value: str) -> bool:
        """Check if a value is a Zoho image download URL (API or files.zohopublic.com)"""
        if not isinstance(value, str):
            return False

        # Pattern for API URLs
        api_pattern = r'/api/v2/.+/report/.+/\d+/.+/download\?filepath=.+\.(png|jpg|jpeg|gif|webp|bmp)'
        if re.search(api_pattern, value, re.IGNORECASE):
            return True

        # Check for files.zohopublic.com URLs
        if 'files.zohopublic.com' in value:
            return True

        return False

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

    def generate_creator_url(self, report_name: str, record_id: str, field_name: str, filename: str, private_key: str = None) -> str:
        """Generate direct Zoho Creator URL for an image"""
        if private_key:
            # Use the provided private key (from files.zohopublic.com transformation)
            return f"https://creatorexport.zoho.com/file/astrastaging/staging-manager/{report_name}/{record_id}/{field_name}/image-download/{private_key}?filepath=/{filename}"
        else:
            # Use the default private key
            return self.base_url.format(
                report_name=report_name,
                record_id=record_id,
                field_name=field_name,
                filename=filename
            )

    def transform_files_zohopublic_url(self, url: str, field_name: str, report_name: str) -> Dict[str, str]:
        """Transform files.zohopublic.com URLs to creatorexport.zoho.com format

        Returns dict with 'url' and 'success' keys
        """
        if not url or 'files.zohopublic.com' not in url:
            return {'url': url, 'success': False}

        try:
            # Parse URL and extract x-cli-msg parameter
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            cli_msg = params.get('x-cli-msg', [None])[0]

            if not cli_msg:
                logger.warning(f"No x-cli-msg parameter in files.zohopublic.com URL")
                return {'url': url, 'success': False}

            # Decode: base64 decode -> URL decode -> parse JSON
            decoded_b64 = base64.b64decode(cli_msg).decode('utf-8')
            decoded_url = unquote(decoded_b64)
            data = json.loads(decoded_url)

            # Extract needed info
            record_id = data.get('recordid')
            filepath = data.get('filepath')
            private_key = data.get('privatekey')

            if not record_id or not filepath or not private_key:
                logger.warning(f"Missing required fields in files.zohopublic.com data: recordid={record_id}, filepath={filepath}, private_key={'***' if private_key else None}")
                return {'url': url, 'success': False}

            # Extract timestamp from filepath (e.g., "1684870719493" from "1684870719493_710")
            timestamp = filepath.split('_')[0]

            # Construct the filename
            filename = f"{timestamp}_{field_name}.jpg"

            # Generate the creatorexport URL using the actual private key
            creator_url = self.generate_creator_url(
                report_name=report_name,
                record_id=record_id,
                field_name=field_name,
                filename=filename,
                private_key=private_key
            )

            logger.debug(f"Transformed files.zohopublic.com URL for {field_name} record {record_id}")
            return {'url': creator_url, 'success': True}

        except Exception as e:
            logger.error(f"Error transforming files.zohopublic.com URL: {e}")
            return {'url': url, 'success': False}

    def process_records_for_urls(self, records: List[Dict], report_name: str, existing_records: Dict[str, Dict] = None) -> Tuple[List[Dict], int]:
        """Process records to replace image URLs with Zoho Creator URLs

        Args:
            records: List of records from Zoho
            report_name: Name of the report
            existing_records: Optional dict of existing records by ID to preserve good URLs

        Returns:
            Tuple of (updated_records, urls_processed_count)
        """
        updated_records: List[Dict] = []
        urls_processed = 0
        urls_skipped = 0

        for record in records:
            updated_record = record.copy()
            record_id = str(record.get('ID', ''))

            if not record_id:
                logger.warning(f"Record missing ID, skipping URL processing")
                updated_records.append(updated_record)
                continue

            # Get existing record if available
            existing_record = existing_records.get(record_id) if existing_records else None

            # Check each field for image URLs
            for field_name, value in record.items():
                if self.is_image_url(value):
                    # SKIP files.zohopublic.com URLs - they return 403 and can't be transformed
                    # Preserve existing creatorexport URLs instead
                    if isinstance(value, str) and 'files.zohopublic.com' in value:
                        # If we have an existing record with a working creatorexport URL, use it
                        if existing_record and field_name in existing_record:
                            existing_url = existing_record[field_name]
                            if existing_url and 'creatorexport.zoho.com' in existing_url:
                                updated_record[field_name] = existing_url
                                urls_skipped += 1
                                logger.debug(f"Preserved existing creatorexport URL for {field_name} in record {record_id}, skipping files.zohopublic.com")
                                continue

                        # Otherwise, keep the files.zohopublic.com URL as-is (will show placeholder in UI)
                        logger.debug(f"Skipping files.zohopublic.com URL for {field_name} in record {record_id} (not accessible)")
                        continue

                    # Handle API URLs
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

                    logger.debug(f"Processed API URL for {field_name} in record {record_id}: {filename}")

            updated_records.append(updated_record)

        if urls_processed > 0 or urls_skipped > 0:
            logger.info(f"Processed {urls_processed} image URLs, skipped {urls_skipped} files.zohopublic.com URLs for {len(records)} records")

        return updated_records, urls_processed

# Global instance
image_url_processor = ImageURLProcessor()
