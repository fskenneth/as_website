#!/usr/bin/env python3
"""
Script to test all image URLs and identify which ones can't load
"""

import sqlite3
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def test_image_url(url, timeout=10):
    """Test if an image URL is accessible"""
    if not url or url == 'blank.png' or not url.startswith('http'):
        return False, "Invalid URL format"

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, "OK"
        elif response.status_code == 403:
            return False, "Forbidden (403)"
        elif response.status_code == 404:
            return False, "Not Found (404)"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def test_all_images():
    """Test all image URLs in the database"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "zoho_sync.db")

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all unique image URLs
    query = """
        SELECT DISTINCT Item_Name, Resized_Image, Item_Image
        FROM Item_Report
        WHERE (Resized_Image IS NOT NULL AND Resized_Image != '' AND Resized_Image != 'blank.png')
           OR (Item_Image IS NOT NULL AND Item_Image != '' AND Item_Image != 'blank.png')
        ORDER BY Item_Name
    """

    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()

    print(f"\nFound {len(records)} items to test\n")

    failed_images = []
    successful_count = 0
    failed_count = 0

    # Test each image URL
    for idx, record in enumerate(records, 1):
        item_name = record['Item_Name']
        resized_image = record['Resized_Image']
        item_image = record['Item_Image']

        print(f"[{idx}/{len(records)}] Testing: {item_name}")

        # Test Resized_Image
        if resized_image and resized_image != 'blank.png' and resized_image.startswith('http'):
            success, message = test_image_url(resized_image)
            if success:
                print(f"  ✓ Resized_Image: {message}")
                successful_count += 1
            else:
                print(f"  ✗ Resized_Image: {message}")
                failed_images.append({
                    'item': item_name,
                    'type': 'Resized_Image',
                    'url': resized_image[:100] + '...' if len(resized_image) > 100 else resized_image,
                    'error': message
                })
                failed_count += 1

        # Test Item_Image
        if item_image and item_image != 'blank.png' and item_image.startswith('http'):
            success, message = test_image_url(item_image)
            if success:
                print(f"  ✓ Item_Image: {message}")
                successful_count += 1
            else:
                print(f"  ✗ Item_Image: {message}")
                failed_images.append({
                    'item': item_name,
                    'type': 'Item_Image',
                    'url': item_image[:100] + '...' if len(item_image) > 100 else item_image,
                    'error': message
                })
                failed_count += 1

        # Small delay to avoid rate limiting
        if idx % 10 == 0:
            time.sleep(0.5)

    # Print summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total images tested: {successful_count + failed_count}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {failed_count}")
    print(f"{'='*80}")

    if failed_images:
        print(f"\nFAILED IMAGES ({len(failed_images)}):")
        print(f"{'='*80}")
        for fail in failed_images:
            print(f"\nItem: {fail['item']}")
            print(f"Type: {fail['type']}")
            print(f"Error: {fail['error']}")
            print(f"URL: {fail['url']}")
    else:
        print(f"\n🎉 All images loaded successfully!")

if __name__ == "__main__":
    test_all_images()
