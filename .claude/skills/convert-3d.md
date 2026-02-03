# Skill: Convert Items to 3D Models

## When to Use
Use this skill when the user asks to convert items to 3D models, generate 3D models, or anything related to creating 3D GLB files from inventory items. Example triggers:
- "Convert all Accent Chairs to 3D"
- "Generate 3D models for all Sofas"
- "Convert Accent Chair 03093 to 3D"
- "Make 3D models for Dining Tables"

## Overview
This skill queries the `zoho_sync.db` database for items that need 3D models, then runs the standalone converter script for each item. The converter script automates the Tripo3D website via Chrome + AppleScript to generate GLB files.

## Step-by-Step Instructions

### 1. Determine What to Convert
Parse the user's request to identify:
- **Specific item name**: e.g. "Accent Chair 03093" (exact match on `Item_Name`)
- **Item type**: e.g. "Accent Chair", "Sofa", "Dining Table" (match on `Item_Type`)
- **Pattern**: e.g. "all chairs" (use LIKE query on `Item_Type`)

### 2. Query the Database
Run a query against the database to find items needing conversion:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/kennethjin/Desktop/development/as_website/data/zoho_sync.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# For specific item name:
# c.execute(\"\"\"SELECT DISTINCT Item_Name, Item_Type, Model_3D FROM Item_Report WHERE Item_Name = ? AND (Model_3D IS NULL OR Model_3D = '')\"\"\", ('ITEM_NAME_HERE',))

# For item type:
# c.execute(\"\"\"SELECT DISTINCT Item_Name, Item_Type, Model_3D FROM Item_Report WHERE Item_Type = ? AND (Model_3D IS NULL OR Model_3D = '') GROUP BY Item_Name ORDER BY Item_Name\"\"\", ('ITEM_TYPE_HERE',))

# For listing types (to help user choose):
c.execute(\"\"\"SELECT Item_Type, COUNT(DISTINCT Item_Name) as total, SUM(CASE WHEN Model_3D IS NOT NULL AND Model_3D != '' THEN 1 ELSE 0 END) as has_model FROM Item_Report GROUP BY Item_Type ORDER BY total DESC\"\"\")

for row in c.fetchall():
    print(dict(row))
conn.close()
"
```

### 3. Show Summary and Confirm
Before running conversions, show the user:
- Number of distinct item names to convert
- Item type(s) involved
- Ask for confirmation before proceeding

### 4. Run Conversions
Run the converter script for each item. **Run up to 10 concurrently** using background bash processes:

```bash
# For a single item:
python3 tools/model_3d/3d_model_converter.py "Accent Chair 03093"

# For multiple items concurrently (up to 10 at a time):
python3 tools/model_3d/3d_model_converter.py "Item Name 1" &
python3 tools/model_3d/3d_model_converter.py "Item Name 2" &
python3 tools/model_3d/3d_model_converter.py "Item Name 3" &
wait
```

**Important concurrency notes:**
- Each invocation opens its own Chrome window, so they can run in parallel
- Limit to 10 concurrent to avoid overwhelming the system
- If running many items, batch them in groups of 10 and wait between batches
- Use `run_in_background` for Bash tool calls and monitor with `TaskOutput`

### 5. Report Results
After all conversions complete, report:
- Total items attempted
- Successful conversions
- Failed conversions (with item names)
- Items that were skipped (already had Model_3D)

### 6. Verify Database Updates
Optionally verify the database was updated:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/kennethjin/Desktop/development/as_website/data/zoho_sync.db')
c = conn.cursor()
c.execute(\"SELECT Item_Name, Model_3D FROM Item_Report WHERE Item_Name = ? LIMIT 1\", ('ITEM_NAME',))
row = c.fetchone()
print(f'Item: {row[0]}, Model_3D: {row[1]}')
conn.close()
"
```

## Converter Script Location
`tools/model_3d/3d_model_converter.py` (relative to project root)

## Script Flags
- `--skip-db-update`: Don't update the database after conversion
- `--keep-window`: Don't close the Chrome window when done
- `--keep-image`: Don't delete the downloaded source image

## Excluded Item Types
The following item types should NOT be converted to 3D (they are flat/2D items):
- Painting
- Headboard (Queen/King/Full/Single)
- Mattress (Queen/King/Full/Single)
- Bed Frame (Queen/King/Full/Single)

If the user asks to convert one of these types, warn them that these are typically flat items that don't produce good 3D results.

## Database Details
- **Database**: `/Users/kennethjin/Desktop/development/as_website/data/zoho_sync.db`
- **Table**: `Item_Report`
- **Key columns**: `Item_Name`, `Item_Type`, `Resized_Image`, `Item_Image`, `Model_3D`
- **Model output**: `/Users/kennethjin/Desktop/development/as_website/static/models/{sanitized_name}.glb`
- The script updates `Model_3D` for ALL rows with the same `Item_Name`
