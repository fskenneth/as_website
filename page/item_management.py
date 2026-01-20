from fasthtml.common import *
from monsterui.all import *
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple
import json
from starlette.responses import JSONResponse
from tools.zoho_sync.write_service import write_service

# Database path
ZOHO_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "zoho_sync.db")

# Initialize FastHTML app
item_management_app, rt = fast_app(
    live=False,  # Disable live reload for sub-app (main app already has it)
    hdrs=[
        Theme.blue.headers(daisy=True),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
        Style("""
            /* CSS Variables for Themes */
            :root, [data-theme="light"] {
                --bg-primary: #ffffff;
                --bg-secondary: #f8f9fa;
                --bg-card: #ffffff;
                --color-primary: #212529;
                --color-secondary: #6c757d;
                --color-accent: #666666;
                --border-color: #e0e0e0;
                --border-hover: #333333;
                --shadow-color: rgba(0, 0, 0, 0.1);
                --modal-bg: rgba(0, 0, 0, 0.5);
            }

            [data-theme="dark"] {
                --bg-primary: #1a1a1a;
                --bg-secondary: #2d2d2d;
                --bg-card: #242424;
                --color-primary: #f8f9fa;
                --color-secondary: #adb5bd;
                --color-accent: #999999;
                --border-color: #404040;
                --border-hover: #ffffff;
                --shadow-color: rgba(0, 0, 0, 0.3);
                --modal-bg: rgba(0, 0, 0, 0.8);
            }

            html, body {
                background-color: var(--bg-primary) !important;
                color: var(--color-primary) !important;
                transition: background-color 0.3s ease, color 0.3s ease;
            }

            /* Ensure all text elements use the theme colors */
            h1, h2, h3, h4, h5, h6, p, span, div, label, input, select, textarea {
                color: var(--color-primary);
            }

            label, .uk-label {
                color: var(--color-primary) !important;
                border: none !important;
                background: transparent !important;
                box-shadow: none !important;
                padding: 0 !important;
            }

            .container {
                max-width: 1450px; /* Increased max-width for 4 columns */
                margin: 0 auto;
                padding: 20px;
            }

            .item-card {
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                background-color: var(--bg-card);
                box-shadow: 0 2px 4px var(--shadow-color);
            }

            .item-image {
                width: 100%;
                height: 300px;
                object-fit: contain;
                border-radius: 4px;
                margin-bottom: 12px;
                cursor: pointer;
                background-color: white;
            }

            .item-info {
                margin-bottom: 8px;
                font-size: 14px;
            }

            .item-name {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 4px;
            }

            .item-dimensions {
                color: var(--color-secondary);
                font-size: 14px;
            }

            .item-attributes {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin: 8px 0;
            }

            .attribute-tag {
                background-color: var(--bg-secondary);
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }

            .location-section {
                background-color: var(--bg-secondary);
                padding: 8px;
                border-radius: 4px;
                margin: 8px 0;
            }

            .location-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
                font-weight: 500;
            }

            .qr-codes {
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }

            .qr-code-tag {
                background-color: var(--bg-secondary);
                border: 1px solid var(--border-color);
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-family: monospace;
                cursor: pointer;
                color: var(--color-primary);
            }

            .qr-code-tag:hover {
                background-color: var(--color-primary);
                color: var(--bg-primary);
            }

            .filter-section {
                background-color: var(--bg-secondary);
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 24px;
                box-shadow: 0 2px 4px var(--shadow-color);
                border: 1px solid var(--border-color);
            }

            .filter-section h4 {
                color: var(--color-primary) !important;
            }

            .count-badge {
                background-color: var(--color-primary);
                color: var(--bg-primary);
                padding: 2px 6px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }

            .scroll-top-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 999;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: rgba(128, 128, 128, 0.7);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                transition: background-color 0.3s, transform 0.3s;
            }

            .scroll-top-btn:hover {
                background-color: rgba(128, 128, 128, 0.9);
                transform: scale(1.05);
            }

            /* Navigation Menu */
            nav {
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
            }

            nav a {
                text-decoration: none;
                color: var(--color-primary);
                transition: all 0.3s ease;
            }

            nav a:hover {
                transform: translateY(-1px);
            }

            /* Theme Toggle Button */
            .theme-toggle {
                background: none;
                border: 2px solid var(--color-primary);
                border-radius: 50%;
                cursor: pointer;
                padding: 8px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                margin-left: 20px;
            }
            .theme-toggle:hover {
                transform: scale(1.1);
                background: var(--color-primary);
            }
            .theme-toggle:hover .theme-icon {
                stroke: var(--bg-primary);
            }
            .theme-icon {
                width: 20px;
                height: 20px;
                transition: all 0.3s ease;
            }
            .theme-icon.sun { display: block; }
            .theme-icon.moon { display: none; }
            [data-theme="dark"] .theme-icon.sun { display: none; }
            [data-theme="dark"] .theme-icon.moon { display: block; }

            /* Global input styles */
            input[type="text"], input[type="number"], select, textarea {
                background: var(--bg-secondary);
                color: var(--color-primary);
                border: 1px solid var(--border-color);
            }

            /* Fix dropdown menu width to match select field */
            .uk-dropdown {
                min-width: 100% !important;
                width: 100% !important;
            }

            /* 3D Icon Styles */
            .item-3d-icon {
                position: absolute;
                top: 20px;
                left: 22px;
                width: 32px;
                height: 32px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #000000;
                z-index: 10;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }

            .item-3d-icon:hover {
                background: rgba(255, 255, 255, 1);
                transform: scale(1.1);
            }

            .item-3d-icon svg {
                width: 20px;
                height: 20px;
                stroke: #000000;
            }

            /* 3D Modal Styles */
            .model-3d-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: none;
                z-index: 1002;
                justify-content: center;
                align-items: center;
            }

            .model-3d-container {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 800px;
                height: 80vh;
                max-height: 600px;
                position: relative;
                overflow: hidden;
            }

            .model-3d-header {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                padding: 16px 20px;
                background: rgba(255, 255, 255, 0.95);
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 10;
                border-bottom: 1px solid #e0e0e0;
            }

            .model-3d-title {
                font-weight: bold;
                font-size: 18px;
                color: #333;
            }

            .model-3d-close {
                font-size: 28px;
                cursor: pointer;
                color: #666;
                line-height: 1;
                padding: 0 8px;
            }

            .model-3d-close:hover {
                color: #333;
            }

            #model-3d-canvas {
                width: 100%;
                height: 100%;
                background: white;
            }

            .model-3d-controls {
                position: absolute;
                bottom: 16px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 8px;
                background: rgba(255, 255, 255, 0.9);
                padding: 8px 16px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }

            .model-3d-control-btn {
                width: 40px;
                height: 40px;
                background: #f0f0f0;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }

            .model-3d-control-btn:hover {
                background: #e0e0e0;
            }

            .model-3d-control-btn svg {
                width: 20px;
                height: 20px;
                min-width: 20px;
                min-height: 20px;
                flex-shrink: 0;
                stroke: #333;
                display: block;
            }

            .model-3d-controls-divider {
                width: 1px;
                height: 24px;
                background: #d0d0d0;
                margin: 8px 4px;
            }

            .model-3d-brightness-control {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .model-3d-brightness-control svg {
                width: 20px;
                height: 20px;
                stroke: #333;
                flex-shrink: 0;
            }

            .model-3d-brightness-slider {
                width: 80px;
                height: 4px;
                -webkit-appearance: none;
                appearance: none;
                background: #d0d0d0;
                border-radius: 2px;
                outline: none;
            }

            .model-3d-brightness-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #333;
                cursor: pointer;
            }

            .model-3d-brightness-slider::-moz-range-thumb {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #333;
                cursor: pointer;
                border: none;
            }

            .model-3d-loading {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                color: #666;
            }

            .model-3d-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #e0e0e0;
                border-top-color: #333;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 12px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Ensure select elements and their dropdowns have consistent width */
            select, .uk-select, .uk-input-fake {
                width: 100% !important;
            }

            /* Make dropdown position relative to its parent */
            .uk-form-controls {
                position: relative;
            }
        """),
    ],
)


def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(ZOHO_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_items_grouped() -> Dict[str, List[sqlite3.Row]]:
    """Get all items grouped by Item_Name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all items ordered by Item_Name, Current_Location, and Barcode
        cursor.execute("""
            SELECT * FROM Item_Report
            WHERE Item_Name IS NOT NULL AND Item_Name != ''
            ORDER BY Item_Name,
                     CASE WHEN Current_Location LIKE '%3600 Warehouse%' THEN 0 ELSE 1 END,
                     Current_Location,
                     Barcode
        """)

        items = cursor.fetchall()
        conn.close()

        # Group by Item_Name
        grouped_items = {}
        for item in items:
            item_name = item['Item_Name']
            if item_name not in grouped_items:
                grouped_items[item_name] = []
            grouped_items[item_name].append(item)
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return {}

    return grouped_items


def parse_location(location_str: str) -> str:
    """Parse location JSON to get display_value"""
    if not location_str:
        return 'Unknown Location'

    # Check if it's a JSON string
    if location_str.startswith('{') and 'display_value' in location_str:
        try:
            location_data = json.loads(location_str)
            return location_data.get('display_value', location_str)
        except json.JSONDecodeError:
            return location_str
    return location_str


def get_location_groups(items: List[sqlite3.Row]) -> Dict[str, List[sqlite3.Row]]:
    """Group items by location"""
    location_groups = {}
    for item in items:
        location = parse_location(item['Current_Location'])
        if location not in location_groups:
            location_groups[location] = []
        location_groups[location].append(item)
    return location_groups


def get_item_image_url(item: sqlite3.Row) -> str:
    """Get the appropriate image URL for an item"""
    # Check if we have a resized image
    if item['Resized_Image'] and item['Resized_Image'] != 'blank.png':
        # If it's already a full URL (starts with http), use it directly
        if item['Resized_Image'].startswith('http'):
            return item['Resized_Image']
        # Otherwise, return a data URL for white background
        else:
            # Return white background as data URL
            return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect width='300' height='300' fill='white'/%3E%3C/svg%3E"
    # Check if we have an original image
    elif item['Item_Image'] and item['Item_Image'] != 'blank.png':
        # If it's already a full URL (starts with http), use it directly
        if item['Item_Image'].startswith('http'):
            return item['Item_Image']
        # Otherwise, return a data URL for white background
        else:
            # Return white background as data URL
            return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect width='300' height='300' fill='white'/%3E%3C/svg%3E"
    # Default to white background
    else:
        # Return white background as data URL
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect width='300' height='300' fill='white'/%3E%3C/svg%3E"


def get_item_attributes(item: sqlite3.Row) -> List[str]:
    """Get item attributes as a list"""
    attributes = []
    if item['Item_Style']:
        attributes.append(item['Item_Style'])
    if item['Item_Color']:
        attributes.append(item['Item_Color'])
    if item['Item_Tone']:
        attributes.append(item['Item_Tone'])
    if item['Item_Material']:
        attributes.append(item['Item_Material'])
    if item['Item_Size']:
        attributes.append(item['Item_Size'])
    return attributes


def create_item_card(item_name: str, items: List[sqlite3.Row]) -> Div:
    """Create a card for an item group"""
    if not items:
        return Div()

    # Use the first item for display
    first_item = items[0]

    # Get dimensions
    width = first_item['Item_Width'] or '0'
    height = first_item['Item_Height'] or '0'
    depth = first_item['Item_Depth'] or '0'
    dimensions = f"{width}x{height}x{depth}"

    # Get counts
    warehouse_count = len([i for i in items if '3600 Warehouse' in parse_location(i['Current_Location'])])
    total_count = len(items)

    # Get attributes
    attributes = get_item_attributes(first_item)

    # Group by location
    location_groups = get_location_groups(items)

    # Create location sections with QR codes
    location_sections = []
    for location, location_items in location_groups.items():
        qr_codes = []
        for item in location_items:
            if item['Barcode']:
                qr_codes.append(
                    Span(
                        item['Barcode'],
                        cls="qr-code-tag",
                        onclick=f"showItemDetails('{item['ID']}')"
                    )
                )

        location_sections.append(
            Div(
                Div(
                    UkIcon("map-pin", height=16, width=16),
                    Span(f"{location} ({len(location_items)})"),
                    cls="location-header"
                ),
                Div(*qr_codes, cls="qr-codes") if qr_codes else Div("No QR codes", style="color: #999; font-size: 12px;"),
                cls="location-section"
            )
        )

    # Check if item has a 3D model
    model_3d = first_item['Model_3D'] if 'Model_3D' in first_item.keys() else None
    has_3d_model = model_3d and model_3d.strip()

    # Get dimensions for 3D model
    item_width = first_item['Item_Width'] or 0
    item_height = first_item['Item_Height'] or 0
    item_depth = first_item['Item_Depth'] or 0

    return Div(
        # 3D Icon (top-left, only shown if item has 3D model)
        Div(
            NotStr('''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>'''),
            cls="item-3d-icon",
            onclick=f"show3DModal('{model_3d}', '{item_name}', {item_width}, {item_height}, {item_depth})",
            title="View 3D Model"
        ) if has_3d_model else None,

        # Count badges
        Div(
            Span(str(warehouse_count), cls="count-badge", style="background-color: green; color: white; margin-right: 4px;"),
            Span(str(total_count), cls="count-badge", style="background-color: black; color: white;"),
            style="position: absolute; top: 20px; right: 22px; z-index: 10;"
        ),

        # Item image with lazy loading
        Img(
            src=get_item_image_url(first_item),
            alt=item_name,
            cls="item-image",
            loading="lazy",
            onclick=f"showImageModal('{first_item['ID']}')"
        ),

        # Item name and dimensions
        Div(
            Div(item_name, cls="item-name"),
            Div(dimensions, cls="item-dimensions", style="text-align: right;"),
            cls="item-info",
            style="display: flex; justify-content: space-between; align-items: center;"
        ),

        # Attributes
        Div(
            *[Span(attr, cls="attribute-tag") for attr in attributes],
            cls="item-attributes"
        ) if attributes else None,

        # Location sections
        *location_sections,

        cls="item-card",
        style="position: relative;"
    )


@rt("/")
async def get(request):
    """Main page handler"""

    # Get all grouped items
    grouped_items = get_items_grouped()

    # Get unique item types and locations for filters
    item_types = []
    locations = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT Item_Type FROM Item_Report WHERE Item_Type IS NOT NULL ORDER BY Item_Type")
        item_types = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Current_Location FROM Item_Report WHERE Current_Location IS NOT NULL ORDER BY Current_Location")
        for row in cursor.fetchall():
            parsed_location = parse_location(row[0])
            if parsed_location not in locations:
                locations.append(parsed_location)
        locations.sort()

        conn.close()
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        pass

    return [
        Title("Item Management"),
        # Navigation Menu
        Nav(
            Div(
                Div(
                    A("Item", href="/item_management/", cls="px-4 py-2 bg-blue-500 text-white rounded", style="font-weight: bold;"),
                    A("Zoho Sync", href="/zoho_sync/", cls="px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"),
                    cls="flex gap-2 items-center"
                ),
                # Theme Toggle Button
                Button(
                    Svg(
                        Path(d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"),
                        viewBox="0 0 24 24",
                        fill="none",
                        stroke="currentColor",
                        stroke_width="2",
                        stroke_linecap="round",
                        stroke_linejoin="round",
                        cls="theme-icon sun"
                    ),
                    Svg(
                        Path(d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"),
                        viewBox="0 0 24 24",
                        fill="none",
                        stroke="currentColor",
                        stroke_width="2",
                        stroke_linecap="round",
                        stroke_linejoin="round",
                        cls="theme-icon moon"
                    ),
                    cls="theme-toggle",
                    id="theme-toggle",
                    **{"aria-label": "Toggle theme"}
                ),
                cls="flex justify-between items-center",
                style="margin: 0 auto; max-width: 1450px; width: 100%;"
            ),
            style="background-color: var(--bg-secondary); border-bottom: 1px solid var(--border-color); padding: 10px 20px; margin-bottom: 20px;",
            cls="sticky top-0 z-50"
        ),
        Container(
            H2("Item Management", style="margin-bottom: 24px;"),

            # Filter section
            Div(
                H4("Filters", style="margin-bottom: 16px;"),
                Grid(
                    Div(
                        Label("Search by Name or QR Code", **{"for": "filter_name"}, style="display: block; margin-bottom: 4px;"),
                        Input(
                            type="text",
                            id="filter_name",
                            name="filter_name",
                            placeholder="Enter item name or QR code...",
                            hx_get="/item_management/filter_items",
                            hx_trigger="keyup changed delay:500ms",
                            hx_target="#items-container",
                            hx_include="#filter_type, #filter_location",
                            cls="uk-input",
                            style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-secondary); color: var(--color-primary);"
                        ),
                    ),
                    Div(
                        Label("Item Type", **{"for": "filter_type"}, style="display: block; margin-bottom: 4px;"),
                        NotStr(f'''<select id="filter_type" name="filter_type"
                            hx-get="/item_management/filter_items"
                            hx-trigger="change"
                            hx-target="#items-container"
                            hx-include="#filter_name, #filter_location"
                            style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-secondary); color: var(--color-primary);">
                            <option value="All" selected>All</option>
                            {"".join([f'<option value="{t}">{t}</option>' for t in item_types])}
                        </select>''')
                    ),
                    Div(
                        Label("Location", **{"for": "filter_location"}, style="display: block; margin-bottom: 4px;"),
                        NotStr(f'''<select id="filter_location" name="filter_location"
                            hx-get="/item_management/filter_items"
                            hx-trigger="change"
                            hx-target="#items-container"
                            hx-include="#filter_name, #filter_type"
                            style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-secondary); color: var(--color-primary);">
                            <option value="All" selected>All</option>
                            {"".join([f'<option value="{l}">{l}</option>' for l in locations])}
                        </select>''')
                    ),
                    cols_lg=3
                ),
                cls="filter-section"
            ),

            # Items container
            Div(
                Grid(
                    *[create_item_card(name, items) for name, items in grouped_items.items()],
                    cols_xl=3, cols_lg=3, cols_md=2, cols_sm=1,  # Responsive columns
                    cls="gap-4"
                ) if grouped_items else Div(
                    H3("No Items Found"),
                    P("The Item_Report table doesn't exist yet or is empty."),
                    P("Please go to ", A("Zoho Sync", href="/zoho_sync/"), " and sync the Item_Report first."),
                    style="text-align: center; padding: 40px; background: var(--bg-secondary); border-radius: 8px;"
                ),
                id="items-container"
            ),

            # Scroll to top button
            Div(
                UkIcon("chevron-up", height=24, width=24),
                cls="scroll-top-btn",
                onclick="window.scrollTo({top: 0, behavior: 'smooth'})"
            ),

            cls="mt-4 mb-4"
        ),

        # Item Details Modal
        Div(
            Div(
                Div(
                    Div(
                        H3("Item Details", style="margin: 0; padding: 0;"),
                        Span("×",
                             onclick="closeModal()",
                             style="font-size: 24px; cursor: pointer; color: var(--color-secondary);"),
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"
                    ),
                    Div(id="modal-content", style="max-height: 70vh; overflow-y: auto;"),
                    Div(
                        Button("Save Changes",
                               onclick="saveItemChanges()",
                               style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; margin-right: 10px; cursor: pointer;"),
                        Button("Delete Item",
                               onclick="deleteItem()",
                               style="background-color: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 4px; margin-right: 10px; cursor: pointer;"),
                        Button("Cancel",
                               onclick="closeModal()",
                               style="background-color: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;"),
                        style="display: flex; justify-content: flex-end; margin-top: 20px; gap: 10px;"
                    ),
                    style="background: var(--bg-card); color: var(--color-primary); padding: 30px; border-radius: 8px; width: 90%; max-width: 800px; position: relative;"
                ),
                id="item-modal",
                style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--modal-bg); display: none; z-index: 1000; justify-content: center; align-items: center;"
            )
        ),

        # Image Modal
        Div(
            Div(
                Div(
                    Span("×",
                         onclick="closeImageModal()",
                         style="position: absolute; top: 10px; right: 20px; font-size: 32px; cursor: pointer; color: var(--color-secondary);"),
                    Div(id="image-modal-content", style="display: flex; gap: 10px; justify-content: center; align-items: center;"),
                    style="background: var(--bg-card); color: var(--color-primary); padding: 20px; border-radius: 8px; width: 95%; max-width: 95vw; position: relative;"
                ),
                id="image-modal",
                style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--modal-bg); display: none; z-index: 1001; justify-content: center; align-items: center;"
            )
        ),

        # 3D Model Modal
        Div(
            Div(
                Div(
                    Span("3D Model", cls="model-3d-title", id="model-3d-title"),
                    Span("×", cls="model-3d-close", onclick="close3DModal()"),
                    cls="model-3d-header"
                ),
                Div(
                    Div(cls="model-3d-spinner"),
                    Span("Loading 3D model..."),
                    cls="model-3d-loading",
                    id="model-3d-loading"
                ),
                Div(id="model-3d-canvas"),
                Div(
                    Button(
                        NotStr('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                            <path d="M3 3v5h5"/>
                        </svg>'''),
                        cls="model-3d-control-btn",
                        onclick="resetModelView()",
                        title="Reset View"
                    ),
                    Button(
                        NotStr('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="8"/>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                            <line x1="11" y1="8" x2="11" y2="14"/>
                            <line x1="8" y1="11" x2="14" y2="11"/>
                        </svg>'''),
                        cls="model-3d-control-btn",
                        onclick="zoomIn3D()",
                        title="Zoom In"
                    ),
                    Button(
                        NotStr('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="8"/>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                            <line x1="8" y1="11" x2="14" y2="11"/>
                        </svg>'''),
                        cls="model-3d-control-btn",
                        onclick="zoomOut3D()",
                        title="Zoom Out"
                    ),
                    # Divider
                    Div(cls="model-3d-controls-divider"),
                    # Brightness control
                    Div(
                        NotStr('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="5"/>
                            <line x1="12" y1="1" x2="12" y2="3"/>
                            <line x1="12" y1="21" x2="12" y2="23"/>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                            <line x1="1" y1="12" x2="3" y2="12"/>
                            <line x1="21" y1="12" x2="23" y2="12"/>
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                        </svg>'''),
                        Input(
                            type="range",
                            min="0.5",
                            max="3",
                            step="0.1",
                            value="1.5",
                            cls="model-3d-brightness-slider",
                            id="brightness-slider",
                            oninput="adjustBrightness3D(this.value)",
                            title="Adjust Brightness"
                        ),
                        cls="model-3d-brightness-control"
                    ),
                    cls="model-3d-controls"
                ),
                cls="model-3d-container"
            ),
            id="model-3d-modal",
            cls="model-3d-modal",
            onclick="if(event.target === this) close3DModal()"
        ),

        # Add JavaScript for modal handling and enhanced lazy loading
        Script("""
            let currentItemId = null;

            async function showItemDetails(itemId) {
                currentItemId = itemId;
                try {
                    const response = await fetch(`/item_management/get_item_details/${itemId}`);
                    const item = await response.json();

                    if (item.error) {
                        alert('Error: ' + item.error);
                        return;
                    }

                    const modalContent = document.getElementById('modal-content');
                    modalContent.innerHTML = createItemDetailsHTML(item);

                    document.getElementById('item-modal').style.display = 'flex';
                } catch (error) {
                    console.error('Error loading item details:', error);
                    alert('Error loading item details');
                }
            }

            function createItemDetailsHTML(item) {
                return `
                    <div class="grid gap-4">
                        <!-- Row 1: Images -->
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block font-bold mb-2">Original Image</label>
                                <img src="${item.Item_Image}" class="w-full h-auto rounded-lg border cursor-pointer mb-2" style="background-color: white;" onclick="window.open('${item.Item_Image}', '_blank')">
                                <button onclick="downloadImage('${item.Item_Image}', '${item.Item_Name}_original.jpg')" class="w-full px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                    Download Original
                                </button>
                            </div>
                            <div>
                                <label class="block font-bold mb-2">Resized Image</label>
                                <img src="${item.Resized_Image}" class="w-full h-auto rounded-lg border cursor-pointer mb-2" style="background-color: white;" onclick="window.open('${item.Resized_Image}', '_blank')">
                                <button onclick="downloadImage('${item.Resized_Image}', '${item.Item_Name}_resized.jpg')" class="w-full px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                                    Download Resized
                                </button>
                            </div>
                        </div>

                        <!-- Row 2: Basic Information -->
                        <div>
                            <h4 class="font-bold text-lg mb-2">Basic Information</h4>
                            <div class="grid grid-cols-3 gap-4">
                                <div>
                                    <label class="block mb-1">Item Name:</label>
                                    <input type="text" id="edit_Item_Name" value="${item.Item_Name || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Item Type:</label>
                                    <input type="text" id="edit_Item_Type" value="${item.Item_Type || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">QR Code:</label>
                                    <input type="text" id="edit_Barcode" value="${item.Barcode || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                            </div>
                        </div>

                        <!-- Row 3: Attributes -->
                        <div>
                            <h4 class="font-bold text-lg mb-2">Attributes</h4>
                            <div class="grid grid-cols-5 gap-4">
                                <div>
                                    <label class="block mb-1">Style:</label>
                                    <input type="text" id="edit_Item_Style" value="${item.Item_Style || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Color:</label>
                                    <input type="text" id="edit_Item_Color" value="${item.Item_Color || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Tone:</label>
                                    <input type="text" id="edit_Item_Tone" value="${item.Item_Tone || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Material:</label>
                                    <input type="text" id="edit_Item_Material" value="${item.Item_Material || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Size:</label>
                                    <input type="text" id="edit_Item_Size" value="${item.Item_Size || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                            </div>
                        </div>

                        <!-- Row 4: Dimensions -->
                        <div>
                            <h4 class="font-bold text-lg mb-2">Dimensions</h4>
                            <div class="grid grid-cols-3 gap-4">
                                <div>
                                    <label class="block mb-1">Width:</label>
                                    <input type="number" id="edit_Item_Width" value="${item.Item_Width || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Height:</label>
                                    <input type="number" id="edit_Item_Height" value="${item.Item_Height || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                                <div>
                                    <label class="block mb-1">Depth:</label>
                                    <input type="number" id="edit_Item_Depth" value="${item.Item_Depth || ''}" class="w-full p-2 border rounded bg-gray-100 dark:bg-gray-700">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 20px;">
                        <h4>System Information</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; font-size: 14px; color: #666;">
                            <div>ID: ${item.ID}</div>
                            <div>Added: ${item.Added_Time || 'N/A'} by ${item.Added_User || 'N/A'}</div>
                            <div>Modified: ${item.Modified_Time || 'N/A'} by ${item.Modified_User || 'N/A'}</div>
                        </div>
                    </div>
                `;
            }

            async function saveItemChanges() {
                if (!currentItemId) return;

                const formData = {
                    Item_Name: document.getElementById('edit_Item_Name').value,
                    Item_Type: document.getElementById('edit_Item_Type').value,
                    Barcode: document.getElementById('edit_Barcode').value,
                    Item_Width: document.getElementById('edit_Item_Width').value,
                    Item_Height: document.getElementById('edit_Item_Height').value,
                    Item_Depth: document.getElementById('edit_Item_Depth').value,
                    Item_Style: document.getElementById('edit_Item_Style').value,
                    Item_Color: document.getElementById('edit_Item_Color').value,
                    Item_Tone: document.getElementById('edit_Item_Tone').value,
                    Item_Material: document.getElementById('edit_Item_Material').value,
                    Item_Size: document.getElementById('edit_Item_Size').value
                };

                try {
                    const response = await fetch(`/item_management/update_item/${currentItemId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    const result = await response.json();
                    if (result.success) {
                        closeModal();
                        // Refresh the page to show updated data
                        location.reload();
                    } else {
                        alert('Error updating item: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error saving item:', error);
                    alert('Error saving item changes');
                }
            }

            async function deleteItem() {
                if (!currentItemId) return;

                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    return;
                }

                try {
                    const response = await fetch(`/item_management/delete_item/${currentItemId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert('Item deleted successfully!');
                        closeModal();
                        // Refresh the page to show updated data
                        location.reload();
                    } else {
                        alert('Error deleting item: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error deleting item:', error);
                    alert('Error deleting item');
                }
            }

            function closeModal() {
                document.getElementById('item-modal').style.display = 'none';
                currentItemId = null;
            }

            function closeImageModal() {
                document.getElementById('image-modal').style.display = 'none';
            }

            async function downloadImage(imageUrl, filename) {
                try {
                    // Fetch the image
                    const response = await fetch(imageUrl);
                    const blob = await response.blob();

                    // Create a temporary URL for the blob
                    const url = window.URL.createObjectURL(blob);

                    // Create a temporary anchor element and trigger download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename.replace(/[^a-zA-Z0-9._-]/g, '_'); // Sanitize filename
                    document.body.appendChild(a);
                    a.click();

                    // Cleanup
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } catch (error) {
                    console.error('Error downloading image:', error);
                    alert('Error downloading image. You can right-click the image and choose "Save Image As..." instead.');
                }
            }

            // Close modal when clicking outside
            document.addEventListener('DOMContentLoaded', function() {
                const modal = document.getElementById('item-modal');
                if (modal) {
                    modal.addEventListener('click', function(e) {
                        if (e.target === this) {
                            closeModal();
                        }
                    });
                }
                const imageModal = document.getElementById('image-modal');
                if (imageModal) {
                    imageModal.addEventListener('click', function(e) {
                        if (e.target === this) {
                            closeImageModal();
                        }
                    });
                }
            });

            // Transform files.zohopublic.com URLs to creatorexport.zoho.com format
            function transformZohoImageUrl(url, fieldName) {
                if (!url || !url.includes('files.zohopublic.com')) {
                    return url;
                }

                try {
                    // Extract the x-cli-msg parameter
                    const urlObj = new URL(url);
                    const cliMsg = urlObj.searchParams.get('x-cli-msg');
                    if (!cliMsg) return url;

                    // Decode base64 then URL decode
                    const decoded = decodeURIComponent(atob(cliMsg));
                    const data = JSON.parse(decoded);

                    // Extract needed info
                    const recordId = data.recordid;
                    const filepath = data.filepath;
                    const reportName = 'Item_Report';

                    if (!recordId || !filepath) return url;

                    // Extract timestamp from filepath (e.g., "1684870719493" from "1684870719493_710")
                    const timestamp = filepath.split('_')[0];

                    // Construct the working URL format: timestamp_fieldName.jpg
                    const privateKey = 'nRxUJtEBFywkxJJ2RNwqbbG9FTZ8QZ0wzde3u0fh5p58fbPt9Kzr06ntwR9vGeJwO63SOMJtQSMY54X3TzMvP4gqOTR14mDDnZNx';
                    const filename = timestamp + '_' + fieldName + '.jpg';

                    return `https://creatorexport.zoho.com/file/astrastaging/staging-manager/${reportName}/${recordId}/${fieldName}/image-download/${privateKey}?filepath=/${filename}`;
                } catch (e) {
                    console.error('Error transforming URL:', e);
                    return url;
                }
            }

            async function showImageModal(itemId) {
                try {
                    const response = await fetch(`/item_management/get_item_details/${itemId}`);
                    const item = await response.json();

                    if (item.error) {
                        alert('Error: ' + item.error);
                        return;
                    }

                    const imageModalContent = document.getElementById('image-modal-content');
                    // Transform only Item_Image URL (files.zohopublic.com returns 403 for Item_Image but 200 for Resized_Image)
                    const originalUrl = transformZohoImageUrl(item.Item_Image, 'Item_Image');
                    const resizedUrl = item.Resized_Image; // Resized_Image works directly without transformation

                    // Check if both URLs are different and both exist
                    const showBothImages = originalUrl && resizedUrl && originalUrl !== resizedUrl;

                    if (showBothImages) {
                        imageModalContent.innerHTML = `
                            <div id="original-image-container" style="flex: 1; text-align: center;">
                                <label class="block font-bold mb-2">Original Image</label>
                                <img id="original-image" src="${originalUrl}" style="max-width: 100%; max-height: 80vh; background-color: white; border-radius: 4px;" onerror="handleOriginalImageError(this)">
                            </div>
                            <div id="resized-image-container" style="flex: 1; text-align: center;">
                                <label class="block font-bold mb-2">Resized Image</label>
                                <img id="resized-image" src="${resizedUrl}" style="max-width: 100%; max-height: 80vh; background-color: white; border-radius: 4px;" onerror="handleResizedImageError(this)">
                            </div>
                        `;
                    } else {
                        // Only show one image - centered
                        const imageUrl = resizedUrl || originalUrl;
                        imageModalContent.innerHTML = `
                            <div style="width: 100%; display: flex; justify-content: center;">
                                <img src="${imageUrl}" style="max-width: 100%; max-height: 80vh; background-color: white; border-radius: 4px;">
                            </div>
                        `;
                    }

                    document.getElementById('image-modal').style.display = 'flex';
                } catch (error) {
                    console.error('Error loading item images:', error);
                    alert('Error loading item images');
                }
            }

            // Handle original image load errors - hide the original and center the resized
            function handleOriginalImageError(img) {
                const originalContainer = document.getElementById('original-image-container');
                const resizedContainer = document.getElementById('resized-image-container');
                if (originalContainer) {
                    originalContainer.style.display = 'none';
                }
                if (resizedContainer) {
                    resizedContainer.style.flex = 'none';
                    resizedContainer.style.width = '100%';
                    resizedContainer.style.display = 'flex';
                    resizedContainer.style.flexDirection = 'column';
                    resizedContainer.style.alignItems = 'center';
                    // Remove the label when showing single image
                    const label = resizedContainer.querySelector('label');
                    if (label) label.style.display = 'none';
                }
            }

            // Handle resized image load errors - hide the resized and center the original
            function handleResizedImageError(img) {
                const originalContainer = document.getElementById('original-image-container');
                const resizedContainer = document.getElementById('resized-image-container');
                if (resizedContainer) {
                    resizedContainer.style.display = 'none';
                }
                if (originalContainer) {
                    originalContainer.style.flex = 'none';
                    originalContainer.style.width = '100%';
                    originalContainer.style.display = 'flex';
                    originalContainer.style.flexDirection = 'column';
                    originalContainer.style.alignItems = 'center';
                    // Remove the label when showing single image
                    const label = originalContainer.querySelector('label');
                    if (label) label.style.display = 'none';
                }
            }

            // Enhanced lazy loading with Intersection Observer
            document.addEventListener('DOMContentLoaded', function() {
                // Native lazy loading is already enabled with loading="lazy"
                // This is additional optimization for browsers that support it
                if ('loading' in HTMLImageElement.prototype) {
                    // Browser supports native lazy loading
                    console.log('Native lazy loading is supported');
                } else {
                    // Fallback for older browsers
                    const images = document.querySelectorAll('img[loading="lazy"]');
                    const imageObserver = new IntersectionObserver((entries, observer) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                const img = entry.target;
                                img.src = img.dataset.src || img.src;
                                img.classList.remove('lazy');
                                imageObserver.unobserve(img);
                            }
                        });
                    });

                    images.forEach(img => imageObserver.observe(img));
                }
            });

            // Theme Management
            const ThemeManager = {
                init() {
                    this.themeToggle = document.getElementById('theme-toggle');
                    this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

                    // Check for saved theme preference
                    const savedTheme = localStorage.getItem('theme');
                    if (savedTheme) {
                        this.setTheme(savedTheme);
                    } else {
                        // Default to light theme if no preference is saved
                        this.setTheme('light');
                    }

                    // Theme toggle button
                    if (this.themeToggle) {
                        this.themeToggle.addEventListener('click', () => {
                            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                            this.setTheme(newTheme);
                            localStorage.setItem('theme', newTheme);
                        });
                    }
                },

                setTheme(theme) {
                    document.documentElement.setAttribute('data-theme', theme);
                    // Force a style recalculation
                    document.documentElement.style.display = 'none';
                    document.documentElement.offsetHeight; // Trigger reflow
                    document.documentElement.style.display = '';
                }
            };

            // Initialize theme on DOM load
            document.addEventListener('DOMContentLoaded', function() {
                ThemeManager.init();
            });

            // 3D Model Viewer
            let threeJsLoaded = false;
            let scene3D = null;
            let camera3D = null;
            let renderer3D = null;
            let controls3D = null;
            let currentModel3D = null;
            let animationId3D = null;
            let ambientLight3D = null;
            let directionalLight1_3D = null;
            let directionalLight2_3D = null;
            let currentModelFile3D = null;
            let currentBrightness3D = 2.5;

            // Base values for 3D viewer
            const BASE_ROTATION_Y = -Math.PI / 2;  // Front-facing rotation
            const BASE_TILT = 0;                   // No tilt for upright view in 3D viewer
            const BASE_BRIGHTNESS = 2.5;           // Default brightness

            // Load Three.js libraries dynamically
            function loadThreeJs() {
                return new Promise((resolve, reject) => {
                    if (threeJsLoaded) {
                        resolve();
                        return;
                    }

                    // Load Three.js
                    const threeScript = document.createElement('script');
                    threeScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                    threeScript.onload = () => {
                        // Load GLTFLoader
                        const gltfScript = document.createElement('script');
                        gltfScript.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js';
                        gltfScript.onload = () => {
                            // Load OrbitControls
                            const orbitScript = document.createElement('script');
                            orbitScript.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js';
                            orbitScript.onload = () => {
                                threeJsLoaded = true;
                                resolve();
                            };
                            orbitScript.onerror = reject;
                            document.head.appendChild(orbitScript);
                        };
                        gltfScript.onerror = reject;
                        document.head.appendChild(gltfScript);
                    };
                    threeScript.onerror = reject;
                    document.head.appendChild(threeScript);
                });
            }

            // Initialize 3D scene
            function init3DScene(container) {
                const width = container.clientWidth;
                const height = container.clientHeight;

                // Create scene
                scene3D = new THREE.Scene();
                scene3D.background = new THREE.Color(0xffffff);

                // Create camera
                camera3D = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera3D.position.set(0, 1, 3);

                // Create renderer
                renderer3D = new THREE.WebGLRenderer({ antialias: true });
                renderer3D.setSize(width, height);
                renderer3D.setPixelRatio(window.devicePixelRatio);
                renderer3D.outputEncoding = THREE.sRGBEncoding;
                renderer3D.toneMapping = THREE.ACESFilmicToneMapping;
                renderer3D.toneMappingExposure = 1.5;
                container.appendChild(renderer3D.domElement);

                // Add orbit controls
                controls3D = new THREE.OrbitControls(camera3D, renderer3D.domElement);
                controls3D.enableDamping = true;
                controls3D.dampingFactor = 0.05;
                controls3D.minDistance = 0.5;
                controls3D.maxDistance = 10;

                // Add lighting (store references for brightness control)
                ambientLight3D = new THREE.AmbientLight(0xffffff, 0.6);
                scene3D.add(ambientLight3D);

                directionalLight1_3D = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight1_3D.position.set(5, 10, 7.5);
                scene3D.add(directionalLight1_3D);

                directionalLight2_3D = new THREE.DirectionalLight(0xffffff, 0.4);
                directionalLight2_3D.position.set(-5, 5, -5);
                scene3D.add(directionalLight2_3D);

                // Add subtle ground shadow
                const groundGeometry = new THREE.PlaneGeometry(10, 10);
                const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.1 });
                const ground = new THREE.Mesh(groundGeometry, groundMaterial);
                ground.rotation.x = -Math.PI / 2;
                ground.position.y = -0.5;
                scene3D.add(ground);

                // Animation loop
                function animate() {
                    animationId3D = requestAnimationFrame(animate);
                    controls3D.update();
                    renderer3D.render(scene3D, camera3D);
                }
                animate();

                // Handle resize
                window.addEventListener('resize', () => {
                    if (renderer3D && camera3D) {
                        const newWidth = container.clientWidth;
                        const newHeight = container.clientHeight;
                        camera3D.aspect = newWidth / newHeight;
                        camera3D.updateProjectionMatrix();
                        renderer3D.setSize(newWidth, newHeight);
                    }
                });
            }

            // Load 3D model
            function load3DModel(modelFile, itemWidth, itemHeight, itemDepth) {
                const loader = new THREE.GLTFLoader();
                const modelUrl = '/static/models/' + modelFile;

                // Store current model file
                currentModelFile3D = modelFile;

                loader.load(
                    modelUrl,
                    (gltf) => {
                        // Remove old model
                        if (currentModel3D) {
                            scene3D.remove(currentModel3D);
                        }

                        currentModel3D = gltf.scene;

                        // Make materials double-sided
                        currentModel3D.traverse((child) => {
                            if (child.isMesh) {
                                child.material.side = THREE.DoubleSide;
                                if (child.material.map) {
                                    child.material.map.encoding = THREE.sRGBEncoding;
                                }
                            }
                        });

                        // Calculate bounding box and scale
                        const box = new THREE.Box3().setFromObject(currentModel3D);
                        const size = box.getSize(new THREE.Vector3());
                        const center = box.getCenter(new THREE.Vector3());

                        // Scale to fit in view
                        const maxDim = Math.max(size.x, size.y, size.z);
                        const scale = 2 / maxDim;
                        currentModel3D.scale.multiplyScalar(scale);

                        // Center horizontally, but position so bottom (feet) sits at floor level
                        currentModel3D.position.x = -center.x * scale;
                        currentModel3D.position.y = -box.min.y * scale;  // Bottom at y=0
                        currentModel3D.position.z = -center.z * scale;

                        // Calculate model center height for camera target
                        const modelCenterY = (size.y * scale) / 2;

                        // Apply base rotation and tilt
                        currentModel3D.rotation.y = BASE_ROTATION_Y;
                        currentModel3D.rotation.x = BASE_TILT;

                        // Position camera at model center height
                        camera3D.position.set(0, modelCenterY, 4.5);

                        // Set brightness to base
                        currentBrightness3D = BASE_BRIGHTNESS;
                        document.getElementById('brightness-slider').value = BASE_BRIGHTNESS;
                        applyBrightness(BASE_BRIGHTNESS);

                        scene3D.add(currentModel3D);

                        // Hide loading indicator
                        document.getElementById('model-3d-loading').style.display = 'none';

                        // Look at model center, not floor
                        controls3D.target.set(0, modelCenterY, 0);
                        controls3D.update();
                    },
                    (progress) => {
                        // Progress callback
                        console.log('Loading progress:', (progress.loaded / progress.total * 100).toFixed(1) + '%');
                    },
                    (error) => {
                        console.error('Error loading 3D model:', error);
                        document.getElementById('model-3d-loading').innerHTML = '<span style="color: #dc3545;">Error loading 3D model</span>';
                    }
                );
            }

            // Apply brightness to all lights
            function applyBrightness(value) {
                const brightness = parseFloat(value);
                if (ambientLight3D) ambientLight3D.intensity = 0.6 * brightness;
                if (directionalLight1_3D) directionalLight1_3D.intensity = 0.8 * brightness;
                if (directionalLight2_3D) directionalLight2_3D.intensity = 0.4 * brightness;
            }

            // Adjust brightness (called from slider)
            function adjustBrightness3D(value) {
                currentBrightness3D = parseFloat(value);
                applyBrightness(value);
            }

            // Show 3D modal
            async function show3DModal(modelFile, itemName, width, height, depth) {
                const modal = document.getElementById('model-3d-modal');
                const title = document.getElementById('model-3d-title');
                const loading = document.getElementById('model-3d-loading');
                const canvas = document.getElementById('model-3d-canvas');

                // Set title
                title.textContent = itemName + ' - 3D Model';

                // Show modal and loading
                modal.style.display = 'flex';
                loading.style.display = 'block';
                loading.innerHTML = '<div class="model-3d-spinner"></div><span>Loading 3D model...</span>';

                // Clear previous canvas
                canvas.innerHTML = '';

                try {
                    // Load Three.js if not loaded
                    await loadThreeJs();

                    // Initialize scene
                    init3DScene(canvas);

                    // Load model
                    load3DModel(modelFile, width, height, depth);
                } catch (error) {
                    console.error('Error initializing 3D viewer:', error);
                    loading.innerHTML = '<span style="color: #dc3545;">Error initializing 3D viewer</span>';
                }
            }

            // Close 3D modal
            function close3DModal() {
                const modal = document.getElementById('model-3d-modal');
                modal.style.display = 'none';

                // Clean up Three.js resources
                if (animationId3D) {
                    cancelAnimationFrame(animationId3D);
                    animationId3D = null;
                }
                if (renderer3D) {
                    renderer3D.dispose();
                    renderer3D = null;
                }
                if (currentModel3D) {
                    currentModel3D = null;
                }
                scene3D = null;
                camera3D = null;
                controls3D = null;

                // Clear canvas
                document.getElementById('model-3d-canvas').innerHTML = '';
            }

            // Reset model view
            function resetModelView() {
                if (camera3D && controls3D) {
                    camera3D.position.set(0, 0.5, 3);
                    controls3D.target.set(0, 0, 0);
                    controls3D.update();
                }
            }

            // Zoom in
            function zoomIn3D() {
                if (camera3D) {
                    camera3D.position.multiplyScalar(0.8);
                }
            }

            // Zoom out
            function zoomOut3D() {
                if (camera3D) {
                    camera3D.position.multiplyScalar(1.25);
                }
            }
        """)
    ]


@rt("/filter_items")
def filter_items(filter_name: str = "", filter_type: str = "All", filter_location: str = "All"):
    """Filter items based on criteria"""

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query with filters
    query = """
        SELECT * FROM Item_Report
        WHERE Item_Name IS NOT NULL AND Item_Name != ''
    """
    params = []

    if filter_name:
        query += " AND (Item_Name LIKE ? OR Barcode LIKE ?)"
        params.append(f"%{filter_name}%")
        params.append(f"%{filter_name}%")

    if filter_type != "All":
        query += " AND Item_Type = ?"
        params.append(filter_type)

    if filter_location != "All":
        # Need to handle JSON location values
        query += " AND Current_Location LIKE ?"
        params.append(f"%{filter_location}%")

    query += """ ORDER BY Item_Name,
                 CASE WHEN Current_Location LIKE '%3600 Warehouse%' THEN 0 ELSE 1 END,
                 Current_Location,
                 Barcode"""

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()

    # Group filtered items
    grouped_items = {}
    for item in items:
        item_name = item['Item_Name']
        if item_name not in grouped_items:
            grouped_items[item_name] = []
        grouped_items[item_name].append(item)

    # Return filtered grid
    return Grid(
        *[create_item_card(name, items) for name, items in grouped_items.items()],
        cols_xl=3, cols_lg=3, cols_md=2, cols_sm=1,  # Responsive columns
        cls="gap-4"
    )


@rt("/get_item_details/{item_id}")
def get_item_details(item_id: str):
    """Get detailed information for a specific item"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Item_Report WHERE ID = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        return JSONResponse({"error": "Item not found"}, status_code=404)

    # Convert Row to dict and handle None values
    item_dict = dict(item)
    for key, value in item_dict.items():
        if value is None:
            item_dict[key] = ""

    return JSONResponse(item_dict)


@rt("/update_item/{item_id}", methods=["POST"])
async def update_item(item_id: str, request):
    """Update an item's information and queue for Zoho sync"""
    try:
        # Get JSON data from request
        import json
        body = await request.body()
        data = json.loads(body.decode())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current values for tracking changes
        cursor.execute("SELECT * FROM Item_Report WHERE ID = ?", (item_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            old_values = dict(zip(columns, row))
        else:
            old_values = {}

        # Build update query dynamically based on provided fields
        fields_to_update = []
        values = []
        changes_for_zoho = {}

        # Define which fields can be updated
        updateable_fields = [
            'Item_Name', 'Item_Type', 'Barcode',
            'Item_Width', 'Item_Height', 'Item_Depth',
            'Item_Style', 'Item_Color', 'Item_Tone', 'Item_Material', 'Item_Size'
        ]

        for field in updateable_fields:
            if field in data:
                fields_to_update.append(f"{field} = ?")
                values.append(data[field])
                # Track changes for Zoho sync
                if str(data[field]) != str(old_values.get(field, '')):
                    changes_for_zoho[field] = data[field]

        if not fields_to_update:
            return {"error": "No valid fields to update"}, 400

        # Add modified timestamp and user
        modified_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        fields_to_update.append("Modified_Time = ?")
        fields_to_update.append("Modified_User = ?")
        values.extend([modified_time, "web_user"])
        changes_for_zoho['Modified_Time'] = modified_time
        changes_for_zoho['Modified_User'] = "web_user"

        # Add item_id for WHERE clause
        values.append(item_id)

        update_query = f"UPDATE Item_Report SET {', '.join(fields_to_update)} WHERE ID = ?"

        cursor.execute(update_query, values)
        conn.commit()
        conn.close()

        # Queue changes for Zoho sync (non-blocking)
        if changes_for_zoho:
            try:
                await write_service.queue_update(
                    record_id=item_id,
                    report_name='Item_Report',
                    changes=changes_for_zoho,
                    old_values=old_values
                )
            except Exception as sync_error:
                # Log but don't fail the request if queue fails
                print(f"Warning: Failed to queue Zoho sync for {item_id}: {sync_error}")

        # Get pending sync count for this record
        pending_count = await write_service.get_pending_for_record(item_id)

        return JSONResponse({
            "success": True,
            "message": "Item updated successfully",
            "sync_status": "queued" if pending_count > 0 else "synced"
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@rt("/delete_item/{item_id}", methods=["DELETE"])
def delete_item(item_id: str):
    """Delete an item from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if item exists
        cursor.execute("SELECT ID FROM Item_Report WHERE ID = ?", (item_id,))
        if not cursor.fetchone():
            conn.close()
            return JSONResponse({"success": False, "error": "Item not found"}, status_code=404)

        # Delete the item
        cursor.execute("DELETE FROM Item_Report WHERE ID = ?", (item_id,))
        conn.commit()
        conn.close()

        return JSONResponse({"success": True, "message": "Item deleted successfully"})

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@rt("/sync_status")
async def get_sync_status():
    """Get the current Zoho sync status"""
    try:
        status = await write_service.get_sync_status()
        return JSONResponse({
            "success": True,
            "status": status
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@rt("/sync_status/{item_id}")
async def get_item_sync_status(item_id: str):
    """Get sync status for a specific item"""
    try:
        pending = await write_service.get_pending_for_record(item_id)
        return JSONResponse({
            "success": True,
            "item_id": item_id,
            "pending_changes": pending,
            "sync_status": "pending" if pending > 0 else "synced"
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# Export the app
item_management_app_export = item_management_app
