#!/usr/bin/env python3
"""
3D Model Converter - Automates Tripo3D website via Chrome + AppleScript

Converts a single furniture item to a 3D model by:
1. Looking up the item image from the database
2. Downloading the image locally
3. Opening a new Chrome window to Tripo3D
4. Automating the upload, settings, and generation
5. Exporting the GLB file
6. Copying to static/models/ and updating the database

Usage:
    python3 -m tools.model_3d.3d_model_converter "Accent Chair 03093"
    python3 tools/model_3d/3d_model_converter.py "Accent Chair 03093" --skip-db-update
"""

import sys
import os

# Force unbuffered output so progress is visible when piped
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import time
import sqlite3
import subprocess
import shutil
import argparse
import ssl
import urllib.request
from pathlib import Path

# Paths - derived from script location (tools/model_3d/3d_model_converter.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "zoho_sync.db"
MODEL_DIR = PROJECT_ROOT / "static" / "models"
TRIPO_URL = "https://studio.tripo3d.ai/workspace/generate"


def sanitize_name(item_name):
    """Convert item name to filename-safe format: 'Accent Chair 03093' -> 'Accent_Chair_03093'"""
    return item_name.replace(" ", "_").replace("/", "_").replace("\\", "_")


def run_applescript(script):
    """Execute an AppleScript and return stdout"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0 and result.stderr.strip():
        print(f"  AppleScript warning: {result.stderr.strip()}")
    return result.stdout.strip()


def run_applescript_long(script, timeout=300):
    """Execute an AppleScript with a longer timeout"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0 and result.stderr.strip():
        print(f"  AppleScript warning: {result.stderr.strip()}")
    return result.stdout.strip()


def chrome_js(window_id, js_code):
    """Execute JavaScript in a specific Chrome window by ID"""
    # Escape for AppleScript string
    escaped = js_code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    script = f'''
    tell application "Google Chrome"
        tell active tab of window id {window_id}
            execute javascript "{escaped}"
        end tell
    end tell
    '''
    return run_applescript(script)


def chrome_js_long(window_id, js_code, timeout=300):
    """Execute JavaScript in Chrome with a longer timeout"""
    escaped = js_code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    script = f'''
    tell application "Google Chrome"
        tell active tab of window id {window_id}
            execute javascript "{escaped}"
        end tell
    end tell
    '''
    return run_applescript_long(script, timeout=timeout)


def get_item_image(item_name):
    """Query database for item image URL"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Item_Name, Item_Type, Resized_Image, Item_Image, Model_3D
        FROM Item_Report
        WHERE Item_Name = ?
        LIMIT 1
    """, (item_name,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "Item_Name": row["Item_Name"],
        "Item_Type": row["Item_Type"],
        "image_url": row["Resized_Image"] if row["Resized_Image"] else row["Item_Image"],
        "Model_3D": row["Model_3D"]
    }


def download_image(image_url, save_path):
    """Download image from URL to local path"""
    print(f"  Downloading image...")
    # Create SSL context that doesn't verify certificates (macOS Python issue)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # URL-encode non-ASCII characters in the URL path
    from urllib.parse import urlsplit, urlunsplit, quote
    parts = urlsplit(image_url)
    encoded_path = quote(parts.path, safe='/:@!$&\'()*+,;=')
    encoded_query = quote(parts.query, safe='/:@!$&\'()*+,;=?')
    image_url = urlunsplit((parts.scheme, parts.netloc, encoded_path, encoded_query, parts.fragment))
    req = urllib.request.Request(image_url)
    with urllib.request.urlopen(req, context=ctx) as response:
        with open(str(save_path), "wb") as f:
            f.write(response.read())
    size_kb = save_path.stat().st_size / 1024
    print(f"  Saved: {save_path.name} ({size_kb:.0f} KB)")


def open_chrome_window():
    """Open a new Chrome window to Tripo3D and return the window ID"""
    print(f"  Opening new Chrome window...")

    script = f'''
    tell application "Google Chrome"
        set newWindow to make new window
        set URL of active tab of newWindow to "{TRIPO_URL}"
        set winId to id of newWindow
        return winId
    end tell
    '''
    window_id = run_applescript(script)
    print(f"  Chrome window ID: {window_id}")

    # Wait for page to load
    print(f"  Waiting for page to load...")
    time.sleep(5)

    # Poll until the page has the upload area
    for attempt in range(30):
        result = chrome_js(window_id, "document.querySelector('input[type=\"file\"]') ? 'ready' : 'loading'")
        if result == "ready":
            print(f"  Page loaded.")
            return window_id
        time.sleep(1)

    print(f"  WARNING: Page may not be fully loaded, continuing anyway...")
    return window_id


def upload_image(window_id, image_path):
    """Upload image to Tripo3D via native file dialog.

    Uses cliclick for a real mouse click on the upload area to trigger the native file
    dialog, then System Events to navigate the dialog and select the file.
    """
    print(f"  Uploading image via file dialog...")

    filepath = str(image_path)

    # All-in-one AppleScript: position window, click upload area, navigate file dialog
    # cliclick is called via do shell script to keep Chrome in foreground
    # Upload area center: screen coords (120, 340) with window at {0, 0, 1440, 900}
    script = f'''
    tell application "Google Chrome"
        activate
        set targetWindow to window id {window_id}
        set index of targetWindow to 1
        set bounds of targetWindow to {{0, 0, 1440, 900}}
    end tell
    delay 1
    -- Click on the upload area center using cliclick
    do shell script "/opt/homebrew/bin/cliclick c:120,340"
    delay 2
    tell application "System Events"
        -- Open "Go to Folder" dialog
        keystroke "g" using {{command down, shift down}}
        delay 1
        -- Type the full file path
        keystroke "{filepath}"
        delay 0.5
        -- Press Enter to navigate to the path
        key code 36
        delay 1.5
        -- Press Enter to select the file
        key code 36
    end tell
    '''
    run_applescript_long(script, timeout=30)
    time.sleep(3)

    # Step 3: Verify the image was uploaded
    for attempt in range(10):
        result = chrome_js(window_id, """
            const imgs = document.querySelectorAll('img[src*=\"blob:\"], img[src*=\"data:\"]');
            const input = document.querySelector('input[type=\"file\"][accept*=\"image\"]');
            const hasFiles = input && input.files && input.files.length > 0;
            hasFiles ? 'uploaded:' + input.files[0].size : imgs.length > 0 ? 'preview_visible' : 'waiting'
        """.replace("\n", " "))

        if result and ("uploaded" in result or "preview_visible" in result):
            print(f"  Image uploaded successfully. ({result})")
            return
        time.sleep(1)

    print(f"  WARNING: Could not confirm upload, continuing anyway...")


def configure_settings(window_id):
    """Click Standard mesh quality and disable 4K Texture"""
    print(f"  Configuring settings...")

    # Click "Standard" mesh quality button
    chrome_js(window_id, """
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim() === 'Standard') {
                buttons[i].click();
                break;
            }
        }
    """.replace("\n", " "))
    time.sleep(0.5)
    print(f"    Mesh Quality: Standard")

    # Expand Texture Settings if collapsed
    # Find the leaf P element with exact text "Texture Settings" and click it
    chrome_js(window_id, """
        var ps = document.querySelectorAll('p');
        for (var i = 0; i < ps.length; i++) {
            if (ps[i].textContent.trim() === 'Texture Settings') {
                ps[i].click();
                break;
            }
        }
    """.replace("\n", " "))
    time.sleep(1)

    # Check if 4K Texture is now visible, if not try clicking the parent div
    has_4k = chrome_js(window_id, """
        var found = false;
        var els = document.querySelectorAll('p, span, div');
        for (var i = 0; i < els.length; i++) {
            if (els[i].textContent.trim() === '4K Texture' && els[i].children.length === 0) {
                found = true;
                break;
            }
        }
        found ? 'visible' : 'hidden'
    """.replace("\n", " "))

    if has_4k != "visible":
        # Try clicking the section/div header instead
        chrome_js(window_id, """
            var ps = document.querySelectorAll('p');
            for (var i = 0; i < ps.length; i++) {
                if (ps[i].textContent.trim() === 'Texture Settings') {
                    var parent = ps[i].parentElement;
                    if (parent) parent.click();
                    break;
                }
            }
        """.replace("\n", " "))
        time.sleep(1)

    # Disable 4K Texture toggle
    # Strategy: find P element with text "4K Texture", walk up to find nearest switch
    result = chrome_js(window_id, """
        var ps = document.querySelectorAll('p');
        var targetP = null;
        for (var i = 0; i < ps.length; i++) {
            if (ps[i].textContent.trim() === '4K Texture') {
                targetP = ps[i];
                break;
            }
        }
        var status = 'no_label';
        if (targetP) {
            var container = targetP;
            var sw = null;
            for (var j = 0; j < 5; j++) {
                container = container.parentElement;
                if (!container) break;
                sw = container.querySelector('button[role=switch]');
                if (sw) break;
            }
            if (sw) {
                if (sw.getAttribute('aria-checked') === 'true') {
                    sw.click();
                    status = 'disabled';
                } else {
                    status = 'already_off';
                }
            } else {
                status = 'no_switch';
            }
        }
        status
    """.replace("\n", " "))
    time.sleep(0.5)

    if result == "disabled":
        print(f"    4K Texture: Disabled")
    elif result == "already_off":
        print(f"    4K Texture: Already off")
    else:
        print(f"    WARNING: Could not find/disable 4K Texture toggle (result: {result})")


def click_generate(window_id):
    """Click the Generate Model button (must cost 25 credits)"""
    print(f"  Clicking Generate Model...")

    # First, check the credit cost on the Generate button
    cost_result = chrome_js(window_id, """
        var target = null;
        var cost = '';
        document.querySelectorAll('button').forEach(function(btn) {
            var t = btn.textContent.trim();
            if (t.indexOf('Generate Model') >= 0 && /[0-9]/.test(t)) {
                target = btn;
                var match = t.match(/([0-9]+)/);
                if (match) { cost = match[1]; }
            }
        });
        cost ? cost : 'not_found'
    """.replace("\n", " "))

    print(f"  Credit cost: {cost_result}")

    if cost_result == "not_found":
        print(f"  ERROR: Could not find Generate Model button with credit cost.")
        sys.exit(1)

    if cost_result != "25":
        print(f"  ERROR: Expected 25 credits but found {cost_result}. Check that 4K Texture is disabled and mesh quality is Standard.")
        sys.exit(1)

    # Cost is 25, safe to click
    chrome_js(window_id, """
        var target = null;
        document.querySelectorAll('button').forEach(function(btn) {
            var t = btn.textContent.trim();
            if (t.indexOf('Generate Model') >= 0 && /[0-9]/.test(t)) {
                target = btn;
            }
        });
        if (target) { target.click(); }
    """.replace("\n", " "))
    time.sleep(2)
    print(f"  Generation started.")


def wait_for_generation(window_id, timeout=600):
    """Poll until the model is generated (Free Retry text appears)"""
    print(f"  Waiting for 3D model generation...")
    start = time.time()

    while time.time() - start < timeout:
        # Check for "Free Retry" text which appears when generation completes
        result = chrome_js(window_id, """
            var bodyText = document.body.textContent;
            var hasRetry = bodyText.indexOf('Free Retry') >= 0;
            var hasFailed = bodyText.indexOf('Generation failed') >= 0 || bodyText.indexOf('Task failed') >= 0;
            hasFailed ? 'failed' : hasRetry ? 'done' : 'generating'
        """.replace("\n", " "))

        elapsed = int(time.time() - start)

        if result == "done":
            print(f"\n  Model generated! ({elapsed}s)")
            return True

        if result == "failed":
            print(f"\n  ERROR: Generation failed!")
            return False

        print(f"  Generating... ({elapsed}s)", end="\r")
        time.sleep(5)

    print(f"\n  ERROR: Generation timed out after {timeout}s")
    return False


def export_model(window_id, filename):
    """Click Export, set filename, and download the GLB"""
    print(f"  Exporting model as: {filename}")

    # Click the Export button in the bottom bar to open the export dialog
    chrome_js(window_id, """
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim() === 'Export') {
                buttons[i].click();
                break;
            }
        }
    """.replace("\n", " "))
    time.sleep(2)

    # Set the filename in the export dialog input
    chrome_js(window_id, """
        var inputs = document.querySelectorAll('input');
        var target = null;
        for (var i = 0; i < inputs.length; i++) {
            var inp = inputs[i];
            if (inp.type === 'text' || !inp.type) {
                var rect = inp.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && rect.top > 100) {
                    target = inp;
                    break;
                }
            }
        }
        if (target) {
            target.focus();
            target.select();
            document.execCommand('selectAll');
            document.execCommand('insertText', false, '""" + filename + """');
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
        }
    """.replace("\n", " "))
    time.sleep(1)

    # Click the Export button inside the dialog (not the bottom bar one)
    # When the dialog is open, the dialog Export button is the LAST one in DOM order
    # (modals are appended at end of body). It also has a smaller top value than bottom bar.
    chrome_js(window_id, """
        var buttons = document.querySelectorAll('button');
        var lastExport = null;
        for (var i = 0; i < buttons.length; i++) {
            var btn = buttons[i];
            if (btn.textContent.trim() === 'Export') {
                var rect = btn.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    lastExport = btn;
                }
            }
        }
        if (lastExport) { lastExport.click(); }
    """.replace("\n", " "))
    time.sleep(2)
    print(f"  Export initiated.")


def wait_for_download(filename, timeout=120):
    """Wait for the GLB file to appear in ~/Downloads or ~/Desktop"""
    print(f"  Waiting for download: {filename}.glb")
    start = time.time()

    search_dirs = [
        Path(os.path.expanduser("~/Downloads")),
        Path(os.path.expanduser("~/Desktop")),
    ]

    while time.time() - start < timeout:
        for search_dir in search_dirs:
            # Check for exact match
            glb_path = search_dir / f"{filename}.glb"
            if glb_path.exists() and glb_path.stat().st_size > 1000:
                print(f"  Found: {glb_path}")
                return glb_path

            # Check for variations (browser might append numbers)
            for f in search_dir.glob(f"{filename}*.glb"):
                if f.stat().st_size > 1000:
                    print(f"  Found: {f}")
                    return f

        elapsed = int(time.time() - start)
        print(f"  Waiting for download... ({elapsed}s)", end="\r")
        time.sleep(2)

    print(f"\n  ERROR: Download timed out after {timeout}s")
    return None


def copy_to_models(glb_path, filename):
    """Copy GLB file to static/models/"""
    dest = MODEL_DIR / f"{filename}.glb"
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(glb_path), str(dest))
    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"  Copied to: {dest} ({size_mb:.1f} MB)")
    return dest


def update_database(item_name, model_filename):
    """Update Model_3D for ALL items with same Item_Name"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Item_Report
        SET Model_3D = ?
        WHERE Item_Name = ?
    """, (model_filename, item_name))

    updated = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"  Database updated: {updated} item(s) set Model_3D = '{model_filename}'")
    return updated


def delete_model_from_tripo(window_id):
    """Delete the most recent model from Tripo3D assets to free storage.

    Navigates to the generate page, clicks the 3-dot menu on the first model,
    clicks Delete, and confirms the deletion.
    """
    print(f"  Navigating to assets page...")

    # Navigate to the generate page to access the assets panel
    chrome_js(window_id, f"window.location.href = '{TRIPO_URL}'")
    time.sleep(5)

    # Wait for the assets panel to load with model cards
    for attempt in range(15):
        result = chrome_js(window_id, """
            var dots = document.querySelectorAll('.i-tripo\\\\:more-horizontal');
            dots.length > 0 ? 'ready:' + dots.length : 'loading'
        """.replace("\n", " "))
        if result and result.startswith("ready"):
            print(f"  Assets loaded. ({result})")
            break
        time.sleep(1)
    else:
        print(f"  WARNING: Could not find model cards in assets panel.")
        return False

    # Click the first 3-dot menu
    chrome_js(window_id, """
        var dots = document.querySelectorAll('.i-tripo\\\\:more-horizontal');
        if (dots.length > 0) dots[0].click();
    """.replace("\n", " "))
    time.sleep(1)

    # Click Delete from the dropdown menu
    chrome_js(window_id, """
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
        while (walker.nextNode()) {
            if (walker.currentNode.textContent.trim() === 'Delete') {
                var parent = walker.currentNode.parentElement;
                var btn = parent.closest('button');
                if (btn && btn.className.indexOf('hover:bg-white-5') >= 0) {
                    btn.click();
                    break;
                }
            }
        }
    """.replace("\n", " "))
    time.sleep(1)

    # Click the confirmation Delete button in the modal
    result = chrome_js(window_id, """
        var buttons = document.querySelectorAll('button');
        var clicked = false;
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim() === 'Delete' && buttons[i].className.indexOf('flex-1') >= 0) {
                buttons[i].click();
                clicked = true;
                break;
            }
        }
        clicked ? 'deleted' : 'not_found'
    """.replace("\n", " "))

    if result == "deleted":
        print(f"  Model deleted from Tripo3D assets.")
        time.sleep(2)  # Wait for deletion to process
        return True
    else:
        print(f"  WARNING: Could not confirm model deletion from Tripo3D.")
        return False


def close_chrome_window(window_id):
    """Close the Chrome window"""
    try:
        script = f'''
        tell application "Google Chrome"
            close window id {window_id}
        end tell
        '''
        run_applescript(script)
        print(f"  Chrome window closed.")
    except Exception as e:
        print(f"  Warning: Could not close Chrome window: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert a single item to 3D model via Tripo3D website")
    parser.add_argument("item_name", help="Item name to convert (e.g. 'Accent Chair 03093')")
    parser.add_argument("--skip-db-update", action="store_true", help="Skip updating the database")
    parser.add_argument("--keep-window", action="store_true", help="Don't close Chrome window when done")
    parser.add_argument("--keep-image", action="store_true", help="Don't delete the downloaded image")

    args = parser.parse_args()
    item_name = args.item_name
    filename = sanitize_name(item_name)

    print(f"\n{'=' * 60}")
    print(f"3D Model Converter")
    print(f"Item: {item_name}")
    print(f"File: {filename}.glb")
    print(f"{'=' * 60}")

    # Step 1: Query database for item image
    print(f"\n[1/10] Looking up item in database...")
    item = get_item_image(item_name)
    if not item:
        print(f"  ERROR: Item '{item_name}' not found in database.")
        sys.exit(1)

    if item["Model_3D"]:
        print(f"  SKIP: Item already has Model_3D = '{item['Model_3D']}'")
        sys.exit(0)

    if not item["image_url"]:
        print(f"  ERROR: No image URL found for '{item_name}'.")
        sys.exit(1)

    print(f"  Type: {item['Item_Type']}")
    print(f"  Image URL: {item['image_url'][:80]}...")

    # Step 2: Download image to static/models/ (temporary, cleaned up after conversion)
    print(f"\n[2/10] Downloading image...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    image_path = MODEL_DIR / f"{filename}.jpg"
    download_image(item["image_url"], image_path)

    window_id = None
    try:
        # Step 3: Open Chrome window
        print(f"\n[3/10] Opening Chrome to Tripo3D...")
        window_id = open_chrome_window()

        # Step 4: Upload image
        print(f"\n[4/10] Uploading image...")
        upload_image(window_id, image_path)

        # Step 5: Configure settings
        print(f"\n[5/10] Configuring generation settings...")
        configure_settings(window_id)

        # Step 6: Generate model
        print(f"\n[6/10] Starting model generation...")
        click_generate(window_id)

        # Step 7: Wait for generation
        print(f"\n[7/10] Waiting for generation to complete...")
        success = wait_for_generation(window_id, timeout=600)
        if not success:
            print(f"  FAILED: Model generation did not complete.")
            sys.exit(1)

        # Step 8: Export model
        print(f"\n[8/10] Exporting model...")
        export_model(window_id, filename)

        # Wait for download
        glb_path = wait_for_download(filename, timeout=120)
        if not glb_path:
            print(f"  FAILED: Could not find downloaded GLB file.")
            sys.exit(1)

        # Copy to static/models/
        copy_to_models(glb_path, filename)

        # Clean up downloaded GLB from Downloads/Desktop
        if glb_path.parent != MODEL_DIR:
            glb_path.unlink()
            print(f"  Cleaned up: {glb_path}")

        # Step 9: Delete model from Tripo3D to free storage
        print(f"\n[9/10] Deleting model from Tripo3D storage...")
        delete_model_from_tripo(window_id)

        # Step 10: Update database
        if not args.skip_db_update:
            print(f"\n[10/10] Updating database...")
            model_filename = f"{filename}.glb"
            update_database(item_name, model_filename)
        else:
            print(f"\n[10/10] Skipping database update (--skip-db-update)")

    finally:
        # Clean up image
        if not args.keep_image and image_path.exists():
            image_path.unlink()
            print(f"  Cleaned up image: {image_path}")

        # Close Chrome window
        if window_id and not args.keep_window:
            close_chrome_window(window_id)

    print(f"\n{'=' * 60}")
    print(f"SUCCESS: {item_name} -> {filename}.glb")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
