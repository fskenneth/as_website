#!/usr/bin/env python3
"""
Script to convert old files.zohopublic.com URLs to new creatorexport.zoho.com format
"""

import sqlite3
import json
import base64
from urllib.parse import urlparse, parse_qs, unquote
import os

def transform_zoho_image_url(url, field_name):
    """Transform files.zohopublic.com URLs to creatorexport.zoho.com format"""
    if not url or 'files.zohopublic.com' not in url:
        return url

    try:
        # Parse URL and extract x-cli-msg parameter
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        cli_msg = params.get('x-cli-msg', [None])[0]

        if not cli_msg:
            print(f"  No x-cli-msg found in URL")
            return url

        # The x-cli-msg is base64 encoded, then URL encoded
        # First base64 decode
        decoded = base64.b64decode(cli_msg).decode('utf-8')
        # Then URL decode to get the JSON
        decoded = unquote(decoded)

        data = json.loads(decoded)

        # Extract needed info
        record_id = data.get('recordid')
        filepath = data.get('filepath')
        private_key = data.get('privatekey')
        report_name = 'Item_Report'

        if not record_id or not filepath or not private_key:
            print(f"  Missing recordid, filepath, or privatekey: recordid={record_id}, filepath={filepath}, privatekey={'***' if private_key else None}")
            return url

        # Extract timestamp from filepath (e.g., "1684870719493" from "1684870719493_710")
        timestamp = filepath.split('_')[0]

        # Get the actual filename from the filepath
        # If filepath contains an actual filename like "1672853471626_Sofa_6764_1920.jpeg", use it
        # Otherwise construct one like "timestamp_fieldname.jpg"
        if '.' in filepath:
            # Use the actual filename from filepath
            filename = filepath.split('/')[-1] if '/' in filepath else filepath
        else:
            filename = f"{timestamp}_{field_name}.jpg"

        new_url = f"https://creatorexport.zoho.com/file/astrastaging/staging-manager/{report_name}/{record_id}/{field_name}/image-download/{private_key}?filepath=/{filename}"

        return new_url

    except Exception as e:
        print(f"  Error transforming URL: {e}")
        return url

def update_database():
    """Update all old format URLs in the database"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "zoho_sync.db")

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find all records with old format URLs
    query = """
        SELECT ID, Item_Name, Resized_Image, Item_Image
        FROM Item_Report
        WHERE Resized_Image LIKE '%files.zohopublic.com%' OR Item_Image LIKE '%files.zohopublic.com%'
    """

    cursor.execute(query)
    records = cursor.fetchall()

    print(f"\nFound {len(records)} records to update")

    updated_count = 0
    failed_count = 0

    for record in records:
        item_id = record['ID']
        item_name = record['Item_Name']
        resized_image = record['Resized_Image']
        item_image = record['Item_Image']

        print(f"\nProcessing: {item_name} (ID: {item_id})")

        new_resized = resized_image
        new_item = item_image

        # Transform Resized_Image if needed
        if resized_image and 'files.zohopublic.com' in resized_image:
            print(f"  Transforming Resized_Image...")
            new_resized = transform_zoho_image_url(resized_image, 'Resized_Image')
            if new_resized != resized_image:
                print(f"  ✓ Resized_Image transformed")
            else:
                print(f"  ✗ Resized_Image transformation failed")
                failed_count += 1

        # Transform Item_Image if needed
        if item_image and 'files.zohopublic.com' in item_image:
            print(f"  Transforming Item_Image...")
            new_item = transform_zoho_image_url(item_image, 'Item_Image')
            if new_item != item_image:
                print(f"  ✓ Item_Image transformed")
            else:
                print(f"  ✗ Item_Image transformation failed")
                failed_count += 1

        # Update the database
        if new_resized != resized_image or new_item != item_image:
            update_query = """
                UPDATE Item_Report
                SET Resized_Image = ?, Item_Image = ?
                WHERE ID = ?
            """
            cursor.execute(update_query, (new_resized, new_item, item_id))
            updated_count += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Update complete!")
    print(f"Total records processed: {len(records)}")
    print(f"Records updated: {updated_count}")
    print(f"Failed transformations: {failed_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    update_database()
