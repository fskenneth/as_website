"""
Batch 3D Model Converter
Converts unique Item_Names to 3D models using Tripo3D API

Usage:
    python3 -m tools.model_3d.batch_convert --item-name "Accent Chair 01052"
    python3 -m tools.model_3d.batch_convert --item-type "Accent Chair" --limit 5
    python3 -m tools.model_3d.batch_convert --item-type "Accent Chair" --dry-run
"""

import asyncio
import argparse
import os
import sys
import json
import uuid
import httpx
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Database and model paths
DB_PATH = PROJECT_ROOT / "data" / "zoho_sync.db"
MODEL_DIR = PROJECT_ROOT / "static" / "models"
HISTORY_FILE = PROJECT_ROOT / "tools" / "model_3d" / "model3d_history.json"
THUMBNAIL_DIR = MODEL_DIR / "thumbnails"

# Ensure directories exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class BatchConverter:
    """Handles batch conversion of items to 3D models"""

    # Item types to exclude from 3D conversion (2D items or simple flat items)
    EXCLUDED_TYPES = [
        'Painting',
        'Headboard Queen',
        'Headboard King',
        'Headboard Full',
        'Headboard Single',
        'Mattress Queen',
        'Mattress King',
        'Mattress Full',
        'Mattress Single',
        'Bed Frame Queen',
        'Bed Frame King',
        'Bed Frame Full',
        'Bed Frame Single',
    ]

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.api_key = os.getenv('TRIPO_API_KEY')
        self.base_url = "https://api.tripo3d.ai/v2/openapi"
        self.stats = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }

    async def get_items_needing_models(
        self,
        item_type: Optional[str] = None,
        item_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get unique Item_Names that don't have 3D models yet"""

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            # Build query for unique item names without models
            query = """
                SELECT
                    Item_Name,
                    Item_Type,
                    COALESCE(
                        NULLIF(Resized_Image, ''),
                        NULLIF(Item_Image, '')
                    ) as image_url,
                    COUNT(*) as item_count,
                    GROUP_CONCAT(ID) as item_ids
                FROM Item_Report
                WHERE (Model_3D IS NULL OR Model_3D = '')
                AND (Resized_Image IS NOT NULL AND Resized_Image != ''
                     OR Item_Image IS NOT NULL AND Item_Image != '')
            """

            params = []

            # Exclude certain item types (paintings, mattresses, bed frames, headboards)
            if self.EXCLUDED_TYPES:
                placeholders = ','.join(['?' for _ in self.EXCLUDED_TYPES])
                query += f" AND Item_Type NOT IN ({placeholders})"
                params.extend(self.EXCLUDED_TYPES)

            if item_name:
                query += " AND Item_Name = ?"
                params.append(item_name)
            elif item_type:
                query += " AND Item_Type = ?"
                params.append(item_type)

            query += " GROUP BY Item_Name ORDER BY Item_Name"

            if limit:
                query += f" LIMIT {limit}"

            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

            return [dict(row) for row in rows]

    async def get_item_by_name(self, item_name: str) -> Optional[Dict]:
        """Get a specific item by name"""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            query = """
                SELECT
                    Item_Name,
                    Item_Type,
                    COALESCE(
                        NULLIF(Resized_Image, ''),
                        NULLIF(Item_Image, '')
                    ) as image_url,
                    COUNT(*) as item_count,
                    GROUP_CONCAT(ID) as item_ids,
                    Model_3D
                FROM Item_Report
                WHERE Item_Name = ?
                GROUP BY Item_Name
            """

            cursor = await db.execute(query, (item_name,))
            row = await cursor.fetchone()

            return dict(row) if row else None

    async def download_image(self, image_url: str) -> bytes:
        """Download image from URL"""
        print(f"  Downloading image from: {image_url[:80]}...")

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(image_url)

            if response.status_code != 200:
                raise Exception(f"Failed to download image: {response.status_code}")

            return response.content

    async def convert_to_3d(self, image_bytes: bytes, item_name: str) -> Dict:
        """Convert image to 3D model using Tripo3D API"""

        if not self.api_key:
            raise Exception("TRIPO_API_KEY not set in environment")

        model_id = uuid.uuid4().hex[:8]
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: Upload image
            print(f"  Uploading image to Tripo3D...")
            upload_response = await client.post(
                f"{self.base_url}/upload",
                headers=headers,
                files={"file": ("image.png", image_bytes, "image/png")}
            )

            if upload_response.status_code != 200:
                raise Exception(f"Upload failed: {upload_response.status_code} - {upload_response.text}")

            upload_data = upload_response.json()
            if upload_data.get("code") != 0:
                raise Exception(f"Upload error: {upload_data}")

            file_token = upload_data["data"]["image_token"]
            print(f"  Image uploaded, token: {file_token[:20]}...")

            # Step 2: Create conversion task
            print(f"  Creating 3D generation task...")
            task_payload = {
                "type": "image_to_model",
                "model_version": "v2.5-20250123",
                "file": {
                    "type": "png",
                    "file_token": file_token
                },
                "pbr": True,
                "enable_image_autofix": True,
                "orientation": "align_image",
                "prompt": "Front facing, legs touching floor level."
            }

            task_response = await client.post(
                f"{self.base_url}/task",
                headers={**headers, "Content-Type": "application/json"},
                json=task_payload
            )

            if task_response.status_code != 200:
                raise Exception(f"Task creation failed: {task_response.status_code} - {task_response.text}")

            task_data = task_response.json()
            if task_data.get("code") != 0:
                raise Exception(f"Task creation error: {task_data}")

            task_id = task_data["data"]["task_id"]
            print(f"  Task created: {task_id}")

            # Step 3: Poll for completion
            print(f"  Waiting for 3D model generation (60-90 seconds)...")
            start_time = datetime.now()

            for attempt in range(180):  # Max 6 minutes
                await asyncio.sleep(2)

                status_response = await client.get(
                    f"{self.base_url}/task/{task_id}",
                    headers=headers
                )

                status_data = status_response.json()
                if status_data.get("code") != 0:
                    raise Exception(f"Status check error: {status_data}")

                task_info = status_data["data"]
                status = task_info["status"]
                progress = task_info.get("progress", 0)

                elapsed = (datetime.now() - start_time).seconds
                print(f"  Status: {status} | Progress: {progress}% | Elapsed: {elapsed}s", end='\r')

                if status == "success":
                    print()  # New line after progress

                    # Step 4: Download model
                    output = task_info.get("output", {})
                    model_url = (output.get("model") or output.get("mesh") or
                                output.get("glb") or output.get("pbr_model") or
                                output.get("base_model"))

                    if not model_url:
                        raise Exception(f"No model URL in output: {output}")

                    print(f"  Downloading model...")
                    model_response = await client.get(model_url)

                    if model_response.status_code != 200:
                        raise Exception(f"Model download failed: {model_response.status_code}")

                    # Save model
                    output_path = MODEL_DIR / f"{model_id}.glb"
                    with open(output_path, 'wb') as f:
                        f.write(model_response.content)

                    file_size = output_path.stat().st_size / (1024 * 1024)
                    processing_time = (datetime.now() - start_time).total_seconds()

                    print(f"  Model saved: {output_path.name} ({file_size:.1f} MB)")

                    # Save thumbnail
                    thumbnail_path = THUMBNAIL_DIR / f"{model_id}_input.png"
                    with open(thumbnail_path, 'wb') as f:
                        f.write(image_bytes)

                    return {
                        'model_id': model_id,
                        'model_filename': f"{model_id}.glb",
                        'model_url': f"/static/models/{model_id}.glb",
                        'format': 'glb',
                        'processing_time': processing_time,
                        'file_size_mb': file_size
                    }

                elif status == "failed":
                    print()
                    raise Exception(f"Task failed: {task_info.get('error', 'Unknown error')}")

                elif status == "banned":
                    print()
                    raise Exception("Task banned - content policy violation")

                elif status == "cancelled":
                    print()
                    raise Exception("Task was cancelled")

            raise Exception("Task timed out after 6 minutes")

    async def update_database(self, item_name: str, model_filename: str):
        """Update all items with the same Item_Name in the database"""

        async with aiosqlite.connect(DB_PATH) as db:
            # Update Model_3D for all items with this Item_Name
            cursor = await db.execute("""
                UPDATE Item_Report
                SET Model_3D = ?
                WHERE Item_Name = ?
            """, (model_filename, item_name))

            updated_count = cursor.rowcount
            await db.commit()

            print(f"  Database updated: {updated_count} item(s) with Model_3D = {model_filename}")

            return updated_count

    async def sync_to_zoho(self, item_name: str, model_filename: str):
        """Sync Model_3D updates to Zoho Creator using the write_service"""
        from tools.zoho_sync.write_service import write_service
        from tools.zoho_sync.database import db as zoho_db

        # Initialize database and write service
        await zoho_db.connect()
        await write_service.init_tables()

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            # Get all item IDs for this Item_Name
            cursor = await db.execute("""
                SELECT ID FROM Item_Report WHERE Item_Name = ?
            """, (item_name,))

            rows = await cursor.fetchall()

        # Queue and process updates for each item
        for row in rows:
            await write_service.queue_update(
                record_id=row['ID'],
                report_name='Item_Report',
                changes={'Model_3D': model_filename},
                old_values={'Model_3D': ''}
            )

        # Process the pending updates immediately
        result = await write_service.process_pending_updates()

        await zoho_db.disconnect()

        print(f"  Zoho sync: {result['processed']} succeeded, {result['failed']} failed")

    def save_to_history(self, item_name: str, result: Dict, image_bytes: bytes):
        """Save conversion to history file"""

        # Load existing history
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except:
                history = []

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "item_name": item_name,
            "input_thumbnail": f"/static/models/thumbnails/{result['model_id']}_input.png",
            "model_url": result['model_url'],
            "format": result['format'],
            "method": "tripo3d",
            "processing_time": result['processing_time'],
            "info": "Tripo3D Pro API - High quality 3D mesh"
        }

        history.insert(0, entry)

        # Save history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

        print(f"  Added to model history")

    async def convert_single_item(self, item_name: str) -> bool:
        """Convert a single item by name"""

        print(f"\n{'='*60}")
        print(f"Converting: {item_name}")
        print(f"{'='*60}")

        # Get item data
        item = await self.get_item_by_name(item_name)

        if not item:
            print(f"  ERROR: Item not found: {item_name}")
            return False

        if item.get('Model_3D'):
            print(f"  SKIP: Already has Model_3D: {item['Model_3D']}")
            self.stats['skipped'] += 1
            return True

        if not item.get('image_url'):
            print(f"  ERROR: No image available for {item_name}")
            return False

        print(f"  Item Type: {item['Item_Type']}")
        print(f"  Items to update: {item['item_count']}")

        if self.dry_run:
            print(f"  [DRY RUN] Would convert this item")
            self.stats['skipped'] += 1
            return True

        try:
            # Download image
            image_bytes = await self.download_image(item['image_url'])

            # Convert to 3D
            result = await self.convert_to_3d(image_bytes, item_name)

            # Update local database
            await self.update_database(item_name, result['model_filename'])

            # Sync to Zoho Creator
            await self.sync_to_zoho(item_name, result['model_filename'])

            # Save to history
            self.save_to_history(item_name, result, image_bytes)

            print(f"\n  SUCCESS: {item_name}")
            print(f"  - Model: {result['model_filename']}")
            print(f"  - Time: {result['processing_time']:.1f}s")
            print(f"  - Size: {result['file_size_mb']:.1f} MB")

            self.stats['success'] += 1
            return True

        except Exception as e:
            print(f"\n  FAILED: {item_name}")
            print(f"  Error: {str(e)}")
            self.stats['failed'] += 1
            return False

        finally:
            self.stats['processed'] += 1

    async def convert_by_type(
        self,
        item_type: str,
        limit: Optional[int] = None
    ) -> Dict:
        """Convert all items of a specific type"""

        print(f"\n{'#'*60}")
        print(f"Batch Converting: {item_type}")
        print(f"{'#'*60}")

        items = await self.get_items_needing_models(item_type=item_type, limit=limit)

        print(f"Found {len(items)} unique item(s) to convert")

        if not items:
            print("No items to convert")
            return self.stats

        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] ", end="")
            await self.convert_single_item(item['Item_Name'])

            # Rate limit: wait between conversions
            if i < len(items) and not self.dry_run:
                print("  Waiting 2s before next conversion...")
                await asyncio.sleep(2)

        return self.stats

    def print_summary(self):
        """Print conversion summary"""
        print(f"\n{'='*60}")
        print("CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"  Processed: {self.stats['processed']}")
        print(f"  Success:   {self.stats['success']}")
        print(f"  Failed:    {self.stats['failed']}")
        print(f"  Skipped:   {self.stats['skipped']}")
        print(f"{'='*60}")


async def main():
    parser = argparse.ArgumentParser(description='Batch convert items to 3D models')
    parser.add_argument('--item-name', type=str, help='Convert specific item by name')
    parser.add_argument('--item-type', type=str, help='Convert all items of this type')
    parser.add_argument('--limit', type=int, help='Limit number of items to convert')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be converted without doing it')
    parser.add_argument('--list-types', action='store_true', help='List all item types and counts')

    args = parser.parse_args()

    # Check for API key
    if not os.getenv('TRIPO_API_KEY') and not args.dry_run and not args.list_types:
        print("ERROR: TRIPO_API_KEY environment variable not set")
        print("Get your API key at: https://platform.tripo3d.ai/api-keys")
        sys.exit(1)

    converter = BatchConverter(dry_run=args.dry_run)

    if args.list_types:
        # List all item types
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT
                    Item_Type,
                    COUNT(DISTINCT Item_Name) as unique_names,
                    SUM(CASE WHEN Model_3D IS NOT NULL AND Model_3D != '' THEN 1 ELSE 0 END) as has_model
                FROM Item_Report
                GROUP BY Item_Type
                ORDER BY unique_names DESC
            """)
            rows = await cursor.fetchall()

            print(f"\n{'Item Type':<25} {'Unique Names':<15} {'Has Model':<10} {'Needs Model':<12} {'Status':<10}")
            print("-" * 80)
            total_needs = 0
            excluded_count = 0
            for row in rows:
                needs = row['unique_names'] - row['has_model']
                is_excluded = row['Item_Type'] in BatchConverter.EXCLUDED_TYPES
                status = "EXCLUDED" if is_excluded else ""
                if is_excluded:
                    excluded_count += needs
                else:
                    total_needs += needs
                print(f"{row['Item_Type']:<25} {row['unique_names']:<15} {row['has_model']:<10} {needs:<12} {status:<10}")
            print("-" * 80)
            print(f"{'TO CONVERT':<25} {'':<15} {'':<10} {total_needs:<12}")
            print(f"{'EXCLUDED':<25} {'':<15} {'':<10} {excluded_count:<12}")
        return

    if args.item_name:
        await converter.convert_single_item(args.item_name)
    elif args.item_type:
        await converter.convert_by_type(args.item_type, limit=args.limit)
    else:
        print("Please specify --item-name or --item-type")
        print("Use --list-types to see available item types")
        parser.print_help()
        sys.exit(1)

    converter.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
