import httpx
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
from urllib.parse import urlparse, parse_qs
import re
from .config import settings
from .zoho_api import zoho_api

logger = logging.getLogger(__name__)

class ImageDownloader:
    def __init__(self):
        self.base_media_path = Path(settings.base_dir) / "media"
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

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

    def get_image_path(self, report_name: str, field_name: str, filename: str) -> Path:
        """Get the local path for storing an image"""
        # Create path: /zoho_sync/media/report_name/field_name/filename
        image_dir = self.base_media_path / report_name / field_name
        image_dir.mkdir(parents=True, exist_ok=True)
        return image_dir / filename

    async def download_image(self, url: str, report_name: str = None, field_name: str = None) -> Optional[str]:
        """Download an image from Zoho and return the local path"""
        try:
            # Extract info from URL if not provided
            if not report_name or not field_name:
                info = self.extract_image_info(url)
                if not info:
                    logger.error(f"Could not extract image info from URL: {url}")
                    return None
                report_name = info['report_name']
                field_name = info['field_name']
                filename = info['filename']
            else:
                # Extract just the filename from URL
                info = self.extract_image_info(url)
                filename = info.get('filename', 'unknown.jpg')

            # Get local path
            local_path = self.get_image_path(report_name, field_name, filename)

            # Skip if already downloaded
            if local_path.exists():
                logger.debug(f"Image already exists: {local_path}")
                return str(local_path.relative_to(settings.base_dir))

            # Build full URL
            if url.startswith('/'):
                full_url = f"{zoho_api.api_domain}{url}"
            else:
                full_url = url

            # Get access token
            access_token = await zoho_api.get_access_token()

            # Download image
            headers = {
                "Authorization": f"Zoho-oauthtoken {access_token}",
            }

            response = await self._client.get(full_url, headers=headers)
            response.raise_for_status()

            # Save image
            local_path.write_bytes(response.content)
            logger.info(f"Downloaded image: {local_path}")

            # Return relative path from base directory
            return str(local_path.relative_to(settings.base_dir))

        except Exception as e:
            logger.error(f"Failed to download image from {url}: {str(e)}")
            return None

    async def download_images_from_records(self, records: List[Dict], report_name: str) -> List[Dict]:
        """Download all images from a list of records and update the records with local paths"""
        updated_records = []

        for record in records:
            updated_record = record.copy()

            # Check each field for image URLs
            for field_name, value in record.items():
                if self.is_image_url(value):
                    logger.debug(f"Found image URL in {field_name}: {value}")

                    # Download the image
                    local_path = await self.download_image(value, report_name, field_name)

                    if local_path:
                        # Update the record with local path
                        updated_record[field_name] = local_path
                        updated_record[f"{field_name}_original_url"] = value

            updated_records.append(updated_record)

        return updated_records

# Global instance
image_downloader = ImageDownloader()
