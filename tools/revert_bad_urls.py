#!/usr/bin/env python3
"""
Revert incorrectly converted image URLs back to NULL
These are URLs with generic filenames like "12345_Resized_Image.jpg"
"""

import sqlite3
import os

def revert_bad_urls():
    """Revert bad URLs with generic filenames"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "zoho_sync.db")

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find and revert URLs with generic filenames
    # Bad pattern: ends with _Resized_Image.jpg or _Item_Image.jpg
    print("\nFinding incorrectly converted URLs...")

    # Count bad URLs
    count_query = """
        SELECT COUNT(*)
        FROM Item_Report
        WHERE (Resized_Image LIKE '%_Resized_Image.jpg'
               OR Resized_Image LIKE '%_Resized_Image.jpeg')
           OR (Item_Image LIKE '%_Item_Image.jpg'
               OR Item_Image LIKE '%_Item_Image.jpeg')
    """

    cursor.execute(count_query)
    bad_count = cursor.fetchone()[0]

    print(f"Found {bad_count} records with incorrectly converted URLs")

    if bad_count == 0:
        print("No bad URLs found. Exiting.")
        conn.close()
        return

    # Revert to blank.png (standard "no image" placeholder)
    print(f"\nReverting {bad_count} bad URLs to 'blank.png'...")

    update_query = """
        UPDATE Item_Report
        SET Resized_Image = 'blank.png',
            Item_Image = 'blank.png'
        WHERE (Resized_Image LIKE '%_Resized_Image.jpg'
               OR Resized_Image LIKE '%_Resized_Image.jpeg')
           OR (Item_Image LIKE '%_Item_Image.jpg'
               OR Item_Image LIKE '%_Item_Image.jpeg')
    """

    cursor.execute(update_query)
    conn.commit()

    print(f"✅ Reverted {cursor.rowcount} records")

    # Verify
    cursor.execute(count_query)
    remaining = cursor.fetchone()[0]

    conn.close()

    print(f"\n{'='*80}")
    print(f"REVERT COMPLETE")
    print(f"{'='*80}")
    print(f"Reverted: {bad_count}")
    print(f"Remaining bad URLs: {remaining}")
    print(f"\n✅ The background page scraper will re-fetch these images from Zoho.")
    print(f"{'='*80}")

if __name__ == "__main__":
    revert_bad_urls()
