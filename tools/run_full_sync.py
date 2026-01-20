#!/usr/bin/env python3
"""
Run a full sync from Zoho to update all image URLs
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.zoho_sync.sync_service import sync_service

async def main():
    """Run full sync"""
    print("="*80)
    print("Starting Full Sync from Zoho Creator")
    print("This will update all image URLs to the correct format")
    print("="*80)

    try:
        # Sync Item_Report (main inventory table)
        print("\nSyncing Item_Report...")
        result = await sync_service.sync_report("Item_Report", sync_type="full")

        print("\n" + "="*80)
        print("SYNC COMPLETE")
        print("="*80)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'no message')}")

        if result.get('status') == 'success':
            print("\n✅ All image URLs have been updated!")
        else:
            print(f"\n❌ Sync failed: {result.get('error', 'unknown error')}")

    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
