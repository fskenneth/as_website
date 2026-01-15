import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from .config import settings
import logging

logger = logging.getLogger(__name__)

class ZohoCreatorAPI:
    def __init__(self):
        self.client_id = settings.zoho_client_id
        self.client_secret = settings.zoho_client_secret
        self.refresh_token = settings.zoho_refresh_token
        self.account_owner = settings.zoho_account_owner_name
        self.app_link_name = settings.zoho_app_link_name
        self.api_domain = settings.zoho_api_domain
        self.base_url = f"{self.api_domain}/api/v2/{self.account_owner}/{self.app_link_name}"
        self.access_token = None
        self.token_expiry = None
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expiry and datetime.utcnow().timestamp() < self.token_expiry:
            return self.access_token

        # Refresh token
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = await self._client.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        # Token expires in 1 hour, refresh 5 minutes early
        self.token_expiry = datetime.utcnow().timestamp() + 3300

        return self.access_token

    async def make_authenticated_request(self, url: str, method: str = "GET",
                                       params: Dict = None, data: Dict = None) -> Dict:
        """Make authenticated request to Zoho Creator API"""
        access_token = await self.get_access_token()

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
        }

        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data
        )

        response.raise_for_status()
        return response.json()

    async def get_report_data(self, report_name: str, criteria: str = None,
                            page: int = 1, page_size: int = 200) -> Dict:
        """Get report data from Zoho Creator"""
        url = f"{self.base_url}/report/{report_name}"

        params = {
            "raw": "true",
            "limit": page_size,
            "from": (page - 1) * page_size + 1,
        }

        if criteria:
            params["criteria"] = criteria

        try:
            response = await self.make_authenticated_request(url, params=params)

            data = response.get("data", [])
            has_more = len(data) == page_size
            total_records = response.get("info", {}).get("count", 0)

            return {
                "data": data,
                "has_more": has_more,
                "total_records": total_records
            }
        except Exception as e:
            logger.error(f"Failed to fetch report {report_name}: {str(e)}")
            raise

    async def get_all_report_data(self, report_name: str, criteria: str = None) -> List[Dict]:
        """Get all records from a report with pagination"""
        all_records = []
        page = 1
        has_more = True

        while has_more:
            result = await self.get_report_data(report_name, criteria, page)
            all_records.extend(result["data"])
            has_more = result["has_more"]
            page += 1

            logger.info(f"Fetched page {page - 1} of {report_name}: {len(result['data'])} records")

        return all_records

    async def get_today_modified_records(self, report_name: str) -> List[Dict]:
        """Get records modified today"""
        # Get today's date in Zoho format (dd-MMM-yyyy)
        today = datetime.now()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        day = today.strftime("%d").lstrip('0')  # Remove leading zero
        month = month_names[today.month - 1]
        year = today.year
        today_str = f"{day}-{month}-{year}"

        # Criteria for records modified today
        criteria = f'Modified_Time == "{today_str}"'

        logger.info(f"Fetching records from {report_name} modified on {today_str}")
        return await self.get_all_report_data(report_name, criteria)

    async def get_modified_records_since(self, report_name: str, since_date: datetime) -> List[Dict]:
        """Get records modified since a specific date"""
        # Convert date to Zoho format
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        day = since_date.strftime("%d")
        month = month_names[since_date.month - 1]
        year = since_date.year
        date_str = f"{day}-{month}-{year}"

        # Criteria for records modified since date
        criteria = f'Modified_Time >= "{date_str}"'

        logger.info(f"Fetching records from {report_name} modified since {date_str}")
        return await self.get_all_report_data(report_name, criteria)

    async def get_report_total_count(self, report_name: str) -> int:
        """Get the total count of records in a report"""
        try:
            # First, try to get metadata which might include count
            metadata = await self.get_report_metadata(report_name)

            # If metadata doesn't provide count, fetch records to count them
            # Note: This is the most reliable way as Zoho API doesn't always
            # provide total count in a separate endpoint
            logger.info(f"Counting total records for {report_name}...")

            # We'll count by fetching all records
            # This ensures accuracy but may take time for large datasets
            total_count = 0
            page = 1
            has_more = True

            while has_more:
                result = await self.get_report_data(report_name, criteria=None, page=page, page_size=200)
                if "data" in result:
                    total_count += len(result["data"])
                    has_more = result.get("has_more", False)
                    page += 1
                else:
                    break

            logger.info(f"Total count for {report_name}: {total_count}")
            return total_count

        except Exception as e:
            logger.error(f"Failed to get total count for {report_name}: {e}")
            return 0

    async def get_report_metadata(self, report_name: str) -> Optional[Dict]:
        """Get report metadata by fetching one record"""
        try:
            result = await self.get_report_data(report_name, page=1, page_size=1)

            if result["data"]:
                sample_record = result["data"][0]
                return {
                    "fields": list(sample_record.keys()),
                    "sample_data": sample_record,
                    "total_records": result["total_records"]
                }

            return None
        except Exception as e:
            logger.error(f"Failed to fetch metadata for {report_name}: {str(e)}")
            raise

    async def list_all_reports(self) -> List[Dict]:
        """List all reports in the Zoho Creator app"""
        try:
            url = f"{self.base_url}/reports"
            response = await self.make_authenticated_request(url)

            if response.get("code") == 3000:
                reports = response.get("reports", [])
                logger.info(f"Found {len(reports)} reports in the app")
                return reports
            else:
                logger.error(f"Failed to list reports: {response}")
                return []
        except Exception as e:
            logger.error(f"Failed to list reports: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test Zoho Creator API connection"""
        try:
            await self.get_access_token()
            # Try to get report list or any simple API call
            # For now, we'll just test the token
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# API instance
zoho_api = ZohoCreatorAPI()
