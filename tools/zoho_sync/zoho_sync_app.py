from fasthtml.common import *
from starlette.requests import Request
from datetime import datetime
import asyncio
import pytz
from .config import settings, validate_config
from .database import db
from .zoho_api import zoho_api
from .sync_service import sync_service
from .image_downloader import image_downloader
import logging
from pathlib import Path
import sys
import os

# Setup logging
Path("./tools/zoho_sync/logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastHTML app
zoho_sync_app, rt = fast_app(
    hdrs=[
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
                margin: 0;
                padding: 0;
                width: 100%;
            }

            /* Navigation Menu */
            nav {
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                width: 100%;
            }

            nav a {
                text-decoration: none !important;
                color: var(--color-primary) !important;
                transition: all 0.3s ease;
            }

            nav a:hover {
                transform: translateY(-1px);
                background-color: var(--bg-secondary) !important;
            }

            /* Active menu item - always white text */
            nav a[href="/zoho_sync/"] {
                color: white !important;
            }

            /* Theme Toggle Button - filled circle */
            .theme-toggle {
                background: var(--color-primary) !important;
                border: none !important;
                border-radius: 50%;
                cursor: pointer;
                padding: 0;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                margin-left: 20px;
            }

            /* Theme toggle colors - white in light mode, black in dark mode */
            [data-theme="light"] .theme-toggle {
                background: white !important;
                border: 2px solid var(--border-color) !important;
            }

            [data-theme="dark"] .theme-toggle {
                background: black !important;
                border: 2px solid var(--border-color) !important;
            }

            .theme-toggle:hover {
                transform: scale(1.1);
            }

            /* Hide Tailwind styling */
            .text-3xl, .text-xl, .text-sm, .text-gray-600, .text-gray-500 {
                all: revert;
            }

            /* Override container max width */
            .container, .max-w-7xl {
                max-width: 1450px !important;
            }

            /* Ensure full width navigation */
            nav {
                width: 100% !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 50 !important;
            }

            nav > div {
                width: 100% !important;
                padding: 0 !important;
            }

            /* Style all text elements */
            h1, h2, h3, h4, h5, h6, p, span, div, label {
                color: var(--color-primary) !important;
            }

            /* Card styling */
            .border {
                border-color: var(--border-color) !important;
            }

            /* Card component */
            .bg-white, .rounded-lg {
                background-color: var(--bg-card) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 8px !important;
                padding: 20px !important;
                margin-bottom: 20px !important;
                box-shadow: 0 2px 4px var(--shadow-color) !important;
            }

            /* Button styling - exclude theme toggle */
            button:not(.theme-toggle), .bg-green-500, .bg-blue-500 {
                background-color: #007bff !important;
                color: white !important;
                border: none !important;
                padding: 8px 16px !important;
                border-radius: 4px !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
            }

            button:not(.theme-toggle):hover, .bg-green-500:hover, .bg-blue-500:hover {
                background-color: #0056b3 !important;
            }

            /* Table styling */
            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                border: 1px solid var(--border-color);
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: var(--bg-secondary);
                font-weight: bold;
            }

            /* Remove all Tailwind container constraints */
            body > * {
                width: 100% !important;
            }

            /* Main container styling */
            .container {
                width: 100% !important;
                max-width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Form and checkbox styling */
            input[type="checkbox"] {
                margin-right: 8px !important;
                margin-left: 4px !important;
                vertical-align: middle !important;
            }

            /* Space out form elements */
            label {
                display: inline-block !important;
                margin-right: 16px !important;
                margin-bottom: 8px !important;
                white-space: nowrap !important;
            }

            /* Button group spacing */
            button {
                margin-right: 10px !important;
                margin-bottom: 10px !important;
            }

            /* Select All / Clear All buttons */
            button[type="button"] {
                margin-right: 10px !important;
            }

            /* Checkbox container */
            div:has(input[type="checkbox"]) {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 10px !important;
                margin: 10px 0 !important;
            }

            /* Card spacing */
            .mb-8, .mb-4 {
                margin-bottom: 24px !important;
            }

            /* Form container */
            form {
                margin: 20px 0 !important;
            }

            /* Report selection area */
            .space-y-2 > div {
                margin-bottom: 16px !important;
            }
        """)
    ]
)

# Initialize database connection when needed
async def ensure_db_connected():
    """Ensure database is connected before operations"""
    if not db._connection:
        await db.connect()

# Note: When mounted as sub-app, startup/shutdown events should be handled by main app

# Helper function to format datetime
def format_datetime(dt_str):
    if not dt_str:
        return "Never"
    try:
        toronto_tz = pytz.timezone(settings.timezone)

        # Parse the datetime string
        if isinstance(dt_str, str):
            # Handle ISO format with 'Z' suffix (UTC)
            if 'Z' in dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            # Handle ISO format with timezone
            elif '+' in dt_str or 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str)
            # Handle SQLite timestamp format (no timezone, assumed UTC)
            else:
                # Try different datetime formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(dt_str, fmt)
                        dt = pytz.UTC.localize(dt)
                        break
                    except ValueError:
                        continue
                else:
                    # If none of the formats work, raise an exception
                    raise ValueError(f"Unable to parse datetime string: {dt_str}")
        else:
            dt = dt_str

        # Convert to Toronto timezone if it has timezone info
        if dt.tzinfo is not None:
            dt = dt.astimezone(toronto_tz)
        else:
            # If no timezone, assume UTC
            dt = pytz.UTC.localize(dt).astimezone(toronto_tz)

        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warning(f"Error formatting datetime {dt_str}: {e}")
        return dt_str

# Main page
@rt("/")
async def get(request):
    await ensure_db_connected()
    sync_status = await sync_service.get_sync_status()
    available_reports = await sync_service.get_available_reports_with_display_names()

    return [
        Title("Zoho Sync AS Dashboard"),
        # Navigation Menu
        Nav(
            Div(
                Div(
                    A("Item", href="/item_management/", style="padding: 8px 16px; background-color: transparent; color: var(--color-primary); border-radius: 4px; text-decoration: none; transition: all 0.3s ease;"),
                    A("Zoho Sync", href="/zoho_sync/", style="padding: 8px 16px; background-color: #007bff; color: white; border-radius: 4px; font-weight: bold; text-decoration: none; transition: all 0.3s ease;"),
                    style="display: flex; gap: 8px; align-items: center;"
                ),
                # Theme Toggle Button
                Button(
                    style="border-radius: 50%; cursor: pointer; padding: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; margin-left: 20px;",
                    cls="theme-toggle",
                    id="theme-toggle",
                    **{"aria-label": "Toggle theme"}
                ),
                style="display: flex; justify-content: space-between; align-items: center; margin: 0 auto; max-width: 1450px; width: 100%;"
            ),
            style="background-color: var(--bg-secondary); border-bottom: 1px solid var(--border-color); padding: 10px 20px; margin-bottom: 20px; position: sticky; top: 0; z-index: 50;"
        ),
        Div(
            # Header
            Div(
                H1("Zoho Sync AS Dashboard", cls="text-3xl font-bold mb-2"),
                P("Sync Astra Staging reports from Zoho Creator to local SQLite database", cls="text-gray-600"),
                P(f"Found {len(available_reports)} reports in astrastaging app", cls="text-sm text-gray-500 mt-1"),
                cls="mb-8"
            ),

            # Configuration Status
            Card(
                H2("Configuration", cls="text-xl font-semibold mb-4"),
                Div(
                    P(f"Account: {settings.zoho_account_owner_name}", cls="text-sm"),
                    P(f"App: {settings.zoho_app_link_name}", cls="text-sm"),
                    P(f"Sync Interval: {settings.sync_interval_minutes} minutes", cls="text-sm"),
                    Button(
                        "Test Connection",
                        hx_post="/zoho_sync/test-connection",
                        hx_target="#connection-status",
                        cls="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mt-2"
                    ),
                    Div(id="connection-status"),
                    cls="space-y-1"
                ),
                cls="mb-8"
            ),

            # Sync Controls
            Card(
                H2("Sync Reports", cls="text-xl font-semibold mb-4"),
                Div(
                    # Report selection
                    Div(
                        Label("Select Reports:", cls="block text-sm font-medium mb-2"),
                        Div(
                            Button(
                                "Select All",
                                type="button",
                                onclick="document.querySelectorAll('[name=reports]').forEach(cb => cb.checked = true)",
                                cls="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 mr-2"
                            ),
                            Button(
                                "Clear All",
                                type="button",
                                onclick="document.querySelectorAll('[name=reports]').forEach(cb => cb.checked = false)",
                                cls="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                            ),
                            cls="mb-2"
                        ),
                        Div(
                            *[
                                Label(
                                    Input(
                                        type="checkbox",
                                        name="reports",
                                        value=report["link_name"],
                                        checked=report["link_name"] in ["Item_Report"],
                                        cls="mr-2"
                                    ),
                                    report["display_name"],
                                    cls="block py-1 hover:bg-gray-100 px-2 rounded cursor-pointer text-sm"
                                )
                                for report in available_reports
                            ],
                            cls="border border-gray-300 rounded p-3 grid grid-cols-3 gap-2"
                        ),
                        cls="mb-4"
                    ),

                    # Sync buttons
                    Div(
                        Button(
                            "Daily Sync (Today's Changes)",
                            hx_post="/zoho_sync/sync/daily",
                            hx_include="[name='reports']:checked",
                            hx_target="#sync-results",
                            hx_indicator="#sync-indicator",
                            hx_vals='js:{reports: Array.from(document.querySelectorAll("[name=reports]:checked")).map(cb => cb.value)}',
                            cls="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-2"
                        ),
                        Button(
                            "Full Sync (All Records)",
                            hx_post="/zoho_sync/sync/full",
                            hx_include="[name='reports']:checked",
                            hx_target="#sync-results",
                            hx_indicator="#sync-indicator",
                            hx_confirm="This will replace all existing data. Are you sure?",
                            hx_vals='js:{reports: Array.from(document.querySelectorAll("[name=reports]:checked")).map(cb => cb.value)}',
                            cls="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 mr-2"
                        ),
                        Span(id="sync-indicator", cls="htmx-indicator ml-4", children="Syncing..."),
                        cls="mb-4"
                    ),
                    Div(id="sync-results"),
                ),
                cls="mb-8"
            ),

            # Report Status
            Card(
                H2("Report Status", cls="text-xl font-semibold mb-4"),
                Div(
                    *[
                        Div(
                            H3(report_name, cls="font-semibold text-lg"),
                            P(f"Records: {info['record_count']}", cls="text-sm text-gray-600"),
                            P(f"Last Modified: {format_datetime(info['last_modified'])}", cls="text-sm text-gray-600"),
                            P(f"Last Sync: {format_datetime(info['last_sync'])}", cls="text-sm text-gray-600"),
                            P(f"Success/Failed: {info['successful_syncs']}/{info['failed_syncs']}", cls="text-sm text-gray-600"),
                            cls="bg-gray-50 p-4 rounded"
                        )
                        for report_name, info in sync_status["reports"].items()
                    ] if sync_status["reports"] else [
                        P("No reports synced yet", cls="text-gray-600")
                    ],
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                )
            ),

            # Recent Sync History
            Card(
                H2("Recent Sync History", cls="text-xl font-semibold mb-4"),
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Time", cls="px-4 py-2"),
                                Th("Type", cls="px-4 py-2"),
                                Th("Report", cls="px-4 py-2"),
                                Th("Status", cls="px-4 py-2"),
                                Th("Records", cls="px-4 py-2"),
                                Th("Error", cls="px-4 py-2")
                            )
                        ),
                        Tbody(
                            *[
                                Tr(
                                    Td(format_datetime(sync["created_at"]), cls="border px-4 py-2"),
                                    Td(sync["sync_type"], cls="border px-4 py-2"),
                                    Td(sync["table_name"], cls="border px-4 py-2"),
                                    Td(
                                        sync["status"],
                                        cls=f"border px-4 py-2 {'text-green-600' if sync['status'] == 'success' else 'text-red-600'}"
                                    ),
                                    Td(str(sync["records_synced"]), cls="border px-4 py-2"),
                                    Td(sync["error_message"] or "-", cls="border px-4 py-2")
                                )
                                for sync in sync_status["recent_syncs"]
                            ] if sync_status["recent_syncs"] else [
                                Tr(Td("No sync history", colspan="6", cls="border px-4 py-2 text-center"))
                            ]
                        ),
                        cls="min-w-full divide-y divide-gray-200"
                    ),
                    cls="overflow-x-auto"
                )
            ),

            # Data Preview
            Card(
                H2("Data Preview", cls="text-xl font-semibold mb-4"),
                Div(
                    Select(
                        Option("Select a report", value=""),
                        *[
                            Option(
                                report["display_name"],
                                value=report["link_name"],
                                selected=report["link_name"] == "Item_Report"
                            )
                            for report in available_reports
                        ],
                        name="table",
                        hx_get="/zoho_sync/data",
                        hx_target="#data-table",
                        hx_trigger="change",
                        cls="border rounded px-3 py-2 w-full md:w-auto"
                    ),
                    cls="mb-4"
                ),
                Div(id="data-table", cls="overflow-x-auto"),
                # Auto-load Item_Report on page load
                Script("htmx.trigger(htmx.find('[name=table]'), 'change')")
            ),

            style="max-width: 1450px; margin: 0 auto; padding: 20px;"
        ),
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Script(src="https://unpkg.com/hyperscript.org@0.9.12"),
        Script("""
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
        """)
    ]

# Test connection endpoint
@rt("/test-connection")
async def post():
    await ensure_db_connected()
    try:
        validate_config()
        result = await zoho_api.test_connection()
        if result:
            return Div(
                P("✅ Connection successful!", cls="text-green-600 mt-2"),
                _="on load wait 3s then remove me"
            )
        else:
            return Div(
                P("❌ Connection failed. Please check your API credentials.", cls="text-red-600 mt-2"),
                _="on load wait 5s then remove me"
            )
    except ValueError as e:
        return Div(
            P(f"❌ Configuration error: {str(e)}", cls="text-red-600 mt-2"),
            _="on load wait 5s then remove me"
        )

# Sync endpoints
@rt("/sync/{sync_type}")
async def post(sync_type: str, request: Request):
    await ensure_db_connected()
    # Get form data
    form_data = await request.form()
    reports = form_data.getlist("reports")

    # If no reports from form, try JSON body
    if not reports:
        try:
            body = await request.json()
            reports = body.get("reports", [])
        except:
            pass

    if not reports:
        return Div(P("Please select at least one report", cls="text-red-600"))

    # Ensure reports is a list
    if isinstance(reports, str):
        reports = [reports]

    result = await sync_service.sync_reports(reports, sync_type)

    return Div(
        Div(
            P(f"Status: {result['status']}",
              cls=f"font-semibold {'text-green-600' if result['status'] == 'success' else 'text-yellow-600'}"),
            P(f"Total records synced: {result['total_records_synced']}"),
            P(f"Total URLs processed: {result.get('total_urls_processed', 0)}"),
            cls="mb-2"
        ),
        *[
            Div(
                P(f"{r['report_name']}: {r['message']}",
                  cls=f"text-sm {'text-green-600' if r['status'] == 'success' else 'text-red-600'}")
            )
            for r in result['results']
        ],
        Button(
            "Refresh Status",
            hx_get="/zoho_sync",
            hx_target="body",
            cls="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 mt-4"
        ),
        cls="bg-gray-50 p-4 rounded"
    )

# Data preview endpoint
@rt("/data")
async def get(table: str = ""):
    await ensure_db_connected()
    if not table:
        return Div(P("Please select a table", cls="text-gray-600"))

    # Sanitize table name
    safe_table = db._sanitize_name(table)

    # Check if table exists
    if not await db.table_exists(safe_table):
        return Div(
            P(f"Table '{table}' has not been synced yet.", cls="text-gray-600 mb-2"),
            P("Please sync this report first using the Sync Reports panel above.", cls="text-sm text-gray-500")
        )

    # Get first 20 records
    query = f"SELECT * FROM {safe_table} LIMIT 20"
    try:
        records = await db.fetchall(query)

        if not records:
            return Div(P(f"No data in {table} table", cls="text-gray-600"))

        # Get column names, excluding system columns
        columns = [col for col in records[0].keys()
                  if not col.startswith('_') and col not in ['ID']]

        # Add ID at the beginning
        display_columns = ['ID'] + columns[:10]  # Limit to 10 columns for display

        return Div(
            P(f"Showing first 20 records from {table}", cls="text-sm text-gray-600 mb-2"),
            Table(
                Thead(
                    Tr(*[Th(col.replace('_', ' ').title(), cls="px-4 py-2 text-left") for col in display_columns])
                ),
                Tbody(
                    *[
                        Tr(
                            *[
                                Td(
                                    # Check if this is an image field (contains media/)
                                    Img(src=f"/{record.get(col, '')}", cls="h-16 w-16 object-cover")
                                    if isinstance(record.get(col, ''), str) and record.get(col, '').startswith('media/') and any(record.get(col, '').endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp'])
                                    else str(record.get(col, ''))[:50] + ('...' if len(str(record.get(col, ''))) > 50 else ''),
                                    cls="border px-4 py-2"
                                )
                                for col in display_columns
                            ],
                            cls="hover:bg-gray-50"
                        )
                        for record in records
                    ]
                ),
                cls="min-w-full divide-y divide-gray-200"
            )
        )
    except Exception as e:
        return Div(P(f"Error loading data: {str(e)}", cls="text-red-600"))

# Serve media files
from starlette.responses import FileResponse

@rt("/media/{filepath:path}")
async def get(filepath: str):
    """Serve media files (images) from the media directory"""
    media_path = Path(settings.base_dir) / "media" / filepath

    if not media_path.exists() or not media_path.is_file():
        return P("File not found", cls="text-red-600")

    # Ensure the path is within the media directory (security)
    try:
        media_path.resolve().relative_to(Path(settings.base_dir) / "media")
    except ValueError:
        return P("Invalid file path", cls="text-red-600")

    return FileResponse(media_path)
