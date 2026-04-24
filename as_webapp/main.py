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
import os

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
from as_webapp.portal_web import staging_task_board
from as_webapp.portal_web import toky_call_intake


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


AUTO_SYNC_ENABLED = True


def _toky_process_one_sync(db_path: str) -> dict | None:
    """One iteration of the Toky worker, pure-sync so it runs cleanly in
    `asyncio.to_thread`. Opens its own sqlite connection (SQLite disallows
    cross-thread connection reuse). Returns the summary dict if a call was
    processed, None if the queue was empty."""
    import sqlite3 as _sqlite
    from as_webapp.as_portal_api import toky_service
    conn = _sqlite.connect(db_path, timeout=30)
    # Let concurrent writers wait instead of failing with "database is
    # locked" — matters when a bulk backfill script is also writing.
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        cdr = toky_service.claim_next_pending(conn)
        if not cdr:
            return None
        try:
            return toky_service.process_call(conn, cdr)
        except Exception as e:
            toky_service.mark_done(
                conn, cdr["callid"], status="error", error=str(e)[:500],
            )
            raise
    finally:
        conn.close()


async def background_toky_worker():
    """Drain toky_calls rows with status='pending': download → Deepgram →
    Sonnet → write derived rows → optional Telegram ping. Runs forever."""
    from as_webapp.as_portal_api.routes import ZOHO_DB_PATH

    print("[Toky Worker] started")
    while True:
        try:
            try:
                summary = await asyncio.to_thread(_toky_process_one_sync, ZOHO_DB_PATH)
            except Exception as e:
                print(f"[Toky Worker] call failed: {e}")
                await asyncio.sleep(3)
                continue

            if summary:
                await _maybe_ping_telegram(summary)
                await _maybe_email_draft(summary)
                print(f"[Toky Worker] {summary.get('callid')} "
                      f"type={summary.get('call_type')} "
                      f"cs={summary.get('cs_task', False)}")
            else:
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Toky Worker] loop error: {e}")
            await asyncio.sleep(10)


async def _maybe_ping_telegram(summary: dict) -> None:
    """Fire a Telegram notification via the configured bot for the calls
    that deserve human eyes. Silent failure — never crash the worker."""
    call_type = summary.get("call_type")
    if not call_type or call_type in ("voicemail_or_failed", "cold_call_inbound", "other"):
        return
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return
    import httpx as _httpx
    emoji = {"customer_service_issue": "🚨", "sales_new_lead": "🟢",
             "sales_follow_up": "📞", "scheduling": "🗓️"}.get(call_type, "📋")
    lines = [
        f"{emoji} *{call_type.replace('_', ' ')}*",
        f"callid: `{summary.get('callid')}`",
        f"{summary.get('summary', '')[:400]}",
    ]
    if summary.get("cs_task"):
        lines.insert(1, "🛠 *CS task auto-created*")
    text = "\n".join(lines)
    try:
        async with _httpx.AsyncClient(timeout=10.0) as c:
            await c.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
    except Exception as e:
        print(f"[Toky Worker] telegram ping failed: {e}")


def _send_draft_email_sync(callid: str) -> None:
    """Send a digest email for a newly-processed Toky call. Handles both
    sales/scheduling (has a staging draft row) and customer-service (has
    a CS task row). Runs inside asyncio.to_thread. Silent on failure.

    Provider choice controlled by TOKY_EMAIL_PROVIDER in .env:
      'gmail' (default) — authentic sales@ mailbox via SMTP; shows in Sent.
      'mailgun'         — legacy path via tools.email_service.
    """
    import json as _json
    import sqlite3 as _sqlite
    provider = os.getenv("TOKY_EMAIL_PROVIDER", "gmail").strip().lower()
    try:
        if provider == "mailgun":
            from tools.email_service import EmailService as _Sender
        else:
            from tools.gmail_sender import GmailSender as _Sender
    except Exception as e:
        print(f"[Toky Worker] email import ({provider}) failed: {e}")
        return

    from as_webapp.as_portal_api.routes import ZOHO_DB_PATH
    conn = _sqlite.connect(ZOHO_DB_PATH)
    conn.row_factory = _sqlite.Row
    try:
        # Prefer the draft (sales/scheduling). Fall back to an empty shell
        # synthesized from the CS task so we still email on complaints.
        draft_row = conn.execute(
            "SELECT * FROM toky_staging_drafts WHERE callid = ? ORDER BY created_at DESC LIMIT 1",
            (callid,),
        ).fetchone()
        cs_row = conn.execute(
            "SELECT * FROM toky_cs_tasks WHERE callid = ? ORDER BY created_at DESC LIMIT 1",
            (callid,),
        ).fetchone()
        if not draft_row and not cs_row:
            return
        draft = dict(draft_row) if draft_row else {
            "callid": callid, "rooms_discussed_json": "[]",
            "next_step": (cs_row["description"] if cs_row else None),
            "zoho_match_hint": None,
        }
        call_row = conn.execute("SELECT * FROM toky_calls WHERE callid = ?", (callid,)).fetchone()
        call = dict(call_row) if call_row else {}
        extract_row = conn.execute(
            "SELECT extract_json FROM toky_extracts WHERE callid = ?", (callid,),
        ).fetchone()
        try:
            extract = _json.loads(extract_row["extract_json"]) if extract_row else {}
        except (TypeError, _json.JSONDecodeError):
            extract = {}
    finally:
        conn.close()

    portal_base = os.getenv("PORTAL_PUBLIC_URL", "http://100.114.47.80:5002")
    portal_link = f"{portal_base}/toky_call_intake/{callid}"

    ct = extract.get("call_type") or "unknown"
    badge = {"sales_new_lead": "#10b981", "sales_follow_up": "#3b82f6",
             "scheduling": "#8b5cf6", "customer_service_issue": "#dc2626",
             }.get(ct, "#6b7280")

    cust = extract.get("customer") if isinstance(extract.get("customer"), dict) else {}
    prop = extract.get("property") if isinstance(extract.get("property"), dict) else {}
    sales_signal = extract.get("sales_signal") if isinstance(extract.get("sales_signal"), dict) else {}
    try:
        rooms = _json.loads(draft.get("rooms_discussed_json") or "[]")
    except Exception:
        rooms = []
    kp = extract.get("key_points") or []
    ai = extract.get("action_items") or []
    obj = sales_signal.get("objections_raised") or []

    kp_html = "".join(f"<li>{k}</li>" for k in kp) or "<li><em>none extracted</em></li>"
    ai_html = "".join(f"<li>{a}</li>" for a in ai) or "<li><em>none</em></li>"
    obj_html = "".join(f"<li>{o}</li>" for o in obj)

    html = f"""<!doctype html><html><body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#111;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:24px 0;"><tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden;">
<tr><td style="padding:22px 28px;border-bottom:1px solid #e4e7eb;">
<div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.08em;font-weight:600;">Toky Call Intake · New draft</div>
<h1 style="margin:4px 0 0;font-size:20px;line-height:1.3;">{(extract.get('summary') or '(no summary)')[:180]}</h1>
<div style="margin-top:8px;">
<span style="display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;color:#fff;background:{badge};text-transform:uppercase;letter-spacing:.03em;">{ct.replace('_',' ')}</span>
<span style="color:#6b7280;font-size:12px;margin-left:6px;">confidence {int((extract.get('confidence') or 0) * 100)}% · {call.get('direction','?')} · {call.get('duration_s','?')}s · agent: {call.get('agent_id','?')}</span>
</div></td></tr>
<tr><td style="padding:18px 28px 4px;">
<h2 style="margin:0 0 6px;font-size:13px;letter-spacing:.04em;color:#6b7280;text-transform:uppercase;">Customer &amp; property</h2>
<table cellpadding="4" cellspacing="0" style="font-size:13px;width:100%;">
<tr><td style="color:#6b7280;width:120px;">name</td><td>{cust.get('name') or '—'}</td></tr>
<tr><td style="color:#6b7280;">phone</td><td>{cust.get('phone') or '—'}</td></tr>
<tr><td style="color:#6b7280;">email</td><td>{cust.get('email') or '—'}</td></tr>
<tr><td style="color:#6b7280;">address</td><td>{prop.get('address') or '—'}</td></tr>
<tr><td style="color:#6b7280;">type</td><td>{prop.get('property_type') or '—'}</td></tr>
<tr><td style="color:#6b7280;">occupancy</td><td>{prop.get('occupancy') or '—'}</td></tr>
<tr><td style="color:#6b7280;">rooms</td><td>{', '.join(rooms) or '—'}</td></tr>
<tr><td style="color:#6b7280;">next step</td><td>{draft.get('next_step') or '—'}</td></tr>
<tr><td style="color:#6b7280;">zoho match</td><td>{draft.get('zoho_match_hint') or '—'}</td></tr>
</table></td></tr>
<tr><td style="padding:18px 28px 4px;">
<h2 style="margin:0 0 6px;font-size:13px;letter-spacing:.04em;color:#6b7280;text-transform:uppercase;">Key points</h2>
<ul style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.55;">{kp_html}</ul></td></tr>
<tr><td style="padding:18px 28px 4px;">
<h2 style="margin:0 0 6px;font-size:13px;letter-spacing:.04em;color:#6b7280;text-transform:uppercase;">Action items</h2>
<ul style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.55;">{ai_html}</ul></td></tr>
{"" if not obj_html else f'<tr><td style="padding:18px 28px 4px;"><h2 style="margin:0 0 6px;font-size:13px;letter-spacing:.04em;color:#6b7280;text-transform:uppercase;">Objections raised</h2><ul style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.55;">{obj_html}</ul></td></tr>'}
<tr><td style="padding:20px 28px 24px;text-align:center;border-top:1px solid #e4e7eb;">
<a href="{portal_link}" style="display:inline-block;padding:10px 22px;background:#3b82f6;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;">Review &amp; approve →</a>
<div style="margin-top:10px;font-size:12px;color:#6b7280;">callid: <code>{callid}</code></div>
</td></tr>
</table></td></tr></table></body></html>"""

    text_body = (
        f"New {ct} draft from Toky.\n\n"
        f"{extract.get('summary', '')}\n\n"
        f"Customer: {cust.get('name','—')}  {cust.get('phone','—')}\n"
        f"Property:  {prop.get('address','—')} ({prop.get('property_type','—')}, {prop.get('occupancy','—')})\n"
        f"Next step: {draft.get('next_step','—')}\n\n"
        f"Review: {portal_link}\n"
    )

    subject = f"[Astra Toky] {ct.replace('_',' ').title()} — {call.get('from_number') or call.get('to_number') or callid[:8]}"
    recipients = [
        r.strip() for r in os.getenv(
            "TOKY_DRAFT_EMAIL_TO",
            "kenneth@astrastaging.com,clara@astrastaging.com",
        ).split(",") if r.strip()
    ]
    try:
        svc = _Sender()
        for to_email in recipients:
            res = svc.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html,
                text_content=text_body,
            )
            if res.get("success"):
                print(f"[Toky Worker] email sent ({provider}) to {to_email} for {callid}: {res.get('message_id')}")
            else:
                print(f"[Toky Worker] email FAILED ({provider}) to {to_email} for {callid}: {res.get('error')}")
    except Exception as e:
        print(f"[Toky Worker] email threw for {callid}: {e}")


async def _maybe_email_draft(summary: dict) -> None:
    """Send a draft digest email for every processed sales/scheduling call
    that produced a staging draft. CS issues also get a notification. Off
    by default unless TOKY_DRAFT_EMAIL_ENABLED is truthy in .env — stops
    us from blasting 500 emails the first time a backfill runs."""
    if os.getenv("TOKY_DRAFT_EMAIL_ENABLED", "").strip().lower() not in ("1", "true", "yes"):
        return
    call_type = summary.get("call_type")
    # Skip noise; only email on calls that produce a draft or CS task.
    if call_type in ("voicemail_or_failed", "cold_call_inbound"):
        return
    callid = summary.get("callid")
    if not callid or summary.get("skipped"):
        return
    await asyncio.to_thread(_send_draft_email_sync, callid)


@app.on_event("startup")
async def startup():
    await zoho_db.connect()
    await write_service.init_tables()

    if AUTO_SYNC_ENABLED:
        # Item_Report is now in SYNC_SCHEDULE (API path) — Playwright page_sync disabled.
        # Zoho WRITE sync intentionally disabled: m4 is the test environment
        # and must never push changes back to the live Zoho Creator tenant.
        # The pending_zoho_updates table can still accumulate rows for
        # debugging, but the drainer stays off.
        _background_tasks.extend([
            # asyncio.create_task(background_zoho_write_sync()),  # DISABLED — read-only
            asyncio.create_task(background_multi_report_sync()),
            asyncio.create_task(background_toky_worker()),
        ])
        print("[Background Sync] Read-only mode. Write sync DISABLED. "
              "Multi-report (Zoho→m4) sync ON. Toky worker ON.")
    else:
        print("[Background Sync] DISABLED (testing mode). Flip AUTO_SYNC_ENABLED in as_webapp/main.py to re-enable.")


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
portal_api.register(rt)               # /api/v1/* (Bearer token — iOS + Android)
portal_web.register(app, rt)          # /signin, /portal, /api/auth/*, admin, 3D, stagings
staging_task_board.register(rt)       # /staging_task_board (+ /stub, /set_date)
toky_call_intake.register(rt)         # /toky_call_intake (+ detail, cs/draft actions)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("as_webapp.main:app", host="0.0.0.0", port=5002, reload=True)
