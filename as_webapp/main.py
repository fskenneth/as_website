"""
as_webapp — Astra Staging internal operations server.

Serves the portal HTML (signin, /portal, admin, 3D designer), the
mobile Bearer-token API (/api/v1/*), and the Zoho sync background
tasks. Kept separate from main.py so the public marketing site stays
up independently of ops.

Run from the repo root (as_website/) so shared imports (tools/, page/)
resolve:

    cd /path/to/as_website
    python3 -m as_webapp.main          # binds to :5002
    ./as_webapp/run.sh                 # same thing
"""
from dotenv import load_dotenv
load_dotenv()

import asyncio

from fasthtml.common import fast_app
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Sub-app mounts (moved from main.py as part of Phase 2)
from page.item_management import item_management_app_export
from page.zoho_sync import zoho_sync_app_export

# Background sync services (moved from main.py as part of Phase 3)
from tools.zoho_sync.database import db as zoho_db
from tools.zoho_sync.zoho_api import zoho_api
from tools.zoho_sync.image_downloader import image_downloader
from tools.zoho_sync.sync_service import sync_service
from tools.zoho_sync.write_service import write_service
from tools.zoho_sync.page_sync_service import PageSyncService

from as_webapp.as_portal_api import routes as portal_api
from as_webapp.portal_web import routes as portal_web


app, rt = fast_app(live=False)


# Static mount — images, CSS, 3D models live in static/. Both servers serve
# them; convenient for the portal designer UI that references /static/models/.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Portal sub-apps
app.mount("/item_management", item_management_app_export)
app.mount("/zoho_sync", zoho_sync_app_export)


@rt("/")
def root():
    """Temporary landing. /signin, /portal, /api/* are the real entry points."""
    return JSONResponse({
        "service": "as_webapp",
        "status": "ok",
        "phase": 3,
        "hints": ["/signin", "/portal", "/api/v1/hello"],
    })


# ---------------- background sync tasks (Phase 3) ----------------

_background_tasks: list = []
_sync_running = False
_page_sync_service: PageSyncService | None = None


async def background_page_sync():
    """Page sync via Playwright (0 API calls). Polls Item_Report every 30s."""
    global _page_sync_service
    _page_sync_service = PageSyncService(poll_interval_seconds=30)
    await _page_sync_service.initialize()

    while True:
        try:
            result = await _page_sync_service.sync_once()
            if result.get("records_synced", 0) > 0:
                print(f"[Page Sync] Synced {result['records_synced']} records (0 API calls)")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Page Sync] Error: {e}")

        await asyncio.sleep(30)


async def background_zoho_write_sync():
    """Drains pending_zoho_updates to Zoho Creator every 30s."""
    while True:
        try:
            await asyncio.sleep(30)
            result = await write_service.process_pending_updates()
            if result["processed"] > 0 or result["failed"] > 0:
                print(f"[Background Sync] Write: {result['processed']} synced, {result['failed']} failed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Background Sync] Write error: {e}")


async def background_multi_report_sync():
    """Incremental sync for reports in config.SYNC_SCHEDULE (60s check cadence)."""
    from tools.zoho_sync.config import SYNC_SCHEDULE
    last_run: dict = {}
    while True:
        try:
            await asyncio.sleep(60)
            now = asyncio.get_event_loop().time()
            due = []
            for report_name, cfg in SYNC_SCHEDULE.items():
                interval_min = cfg.get("interval_minutes", 0)
                if interval_min <= 0:
                    continue
                prev = last_run.get(report_name, 0)
                if (now - prev) >= interval_min * 60:
                    due.append(report_name)

            for report_name in due:
                try:
                    result = await sync_service.sync_report(report_name, sync_type="incremental")
                    last_run[report_name] = asyncio.get_event_loop().time()
                    n = result.get("records_synced", 0)
                    if n > 0:
                        print(f"[Multi Sync] {report_name}: {n} records")
                except Exception as e:
                    print(f"[Multi Sync] {report_name} error: {e}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Multi Sync] Loop error: {e}")


@app.on_event("startup")
async def startup():
    await zoho_db.connect()
    await write_service.init_tables()

    _background_tasks.extend([
        asyncio.create_task(background_page_sync()),
        asyncio.create_task(background_zoho_write_sync()),
        asyncio.create_task(background_multi_report_sync()),
    ])
    print("[Background Sync] Started page sync (30s), write sync (30s), and multi-report sync (60s check) tasks")


@app.on_event("shutdown")
async def shutdown():
    for task in _background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    if _page_sync_service:
        await _page_sync_service.close()

    await zoho_db.disconnect()
    await zoho_api.close()
    await image_downloader.close()


# Register routes
portal_api.register(rt)       # /api/v1/* (Bearer token — iOS + Android)
portal_web.register(app, rt)  # /signin, /portal, /api/auth/*, admin, 3D, stagings


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("as_webapp.main:app", host="0.0.0.0", port=5002, reload=True)
