"""
Anna — internal LLM agent for ops queries.

Phase 1: text-only Q&A grounded in the staging + inventory + employee
context. The next phase will add tool calls (search_items, search_stagings,
update_item, find_customer …) so Anna can actually mutate things on
behalf of an employee. For now she's read-only and only reasons over
data we hand her in the system prompt.
"""
import asyncio
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from . import chat_db
from .chat_bus import bus


ROOT = Path(__file__).resolve().parents[2]
ZOHO_DB_PATH = ROOT / "data" / "zoho_sync.db"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 600
HISTORY_LIMIT = 30  # messages of context we replay to Anna

_client: Anthropic | None = None


def _get_client() -> Anthropic | None:
    global _client
    if _client is not None:
        return _client
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    _client = Anthropic(api_key=key)
    return _client


_SYSTEM_PROMPT = """You are Anna, the in-house operations agent for Astra Staging — a home staging company in the Greater Toronto Area.

You help internal staff (owners, sales, stagers, movers) with quick operational questions: looking up stagings, items, customers, schedules, payroll context, and team logistics. Keep responses concise and action-oriented. Drop pleasantries; the team is busy.

Style:
- Lead with the answer. Reasoning second, only if needed.
- Use plain text. Markdown lists are fine; no headers.
- 1-3 sentences for simple questions. Longer only if the user asks for detail.
- If a question would need data you don't have access to (specific addresses, real-time inventory, payroll figures), say so plainly and suggest which app/screen to open instead — don't make up numbers.
- Refer to people by first name.

You are talking to: {user_first_name} ({user_role}).
Today is {today}.

Active staging snapshot (current week): {staging_summary}
"""


def _build_staging_summary() -> str:
    """Cheap one-liner about the active queue for grounding. No PII."""
    if not ZOHO_DB_PATH.exists():
        return "(staging DB not yet synced)"
    conn = sqlite3.connect(str(ZOHO_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("""
            SELECT
              SUM(CASE WHEN Staging_Status = 'Active' THEN 1 ELSE 0 END) AS active,
              SUM(CASE WHEN Staging_Status = 'Inquired' THEN 1 ELSE 0 END) AS inquired
            FROM Staging_Report
        """).fetchone()
        if not row:
            return "(staging table empty)"
        return f"{row['active'] or 0} active, {row['inquired'] or 0} inquired"
    except sqlite3.Error:
        return "(staging summary unavailable)"
    finally:
        conn.close()


def _format_history(viewer_id: int, anna_id: int, msgs: list[dict]) -> list[dict]:
    """Convert chat rows into the Anthropic Messages format. Viewer's
    messages → 'user'; Anna's messages → 'assistant'."""
    out = []
    for m in msgs:
        role = "assistant" if m["sender_id"] == anna_id else "user"
        out.append({"role": role, "content": m["body"]})
    # The Messages API requires alternating roles. Coalesce consecutive
    # same-role messages so a user double-tap doesn't reject the request.
    coalesced: list[dict] = []
    for entry in out:
        if coalesced and coalesced[-1]["role"] == entry["role"]:
            coalesced[-1]["content"] += "\n\n" + entry["content"]
        else:
            coalesced.append(entry)
    return coalesced


async def respond(conv_id: int, viewer_id: int, viewer: dict) -> None:
    """Generate Anna's reply for the latest message in `conv_id`, persist
    it, and publish over the SSE bus. Safe to fire-and-forget; logs and
    swallows failures so a 500 from Claude doesn't break the chat."""
    client = _get_client()
    if client is None:
        _post_anna_message(conv_id, viewer_id, viewer,
                           "(Anna is not configured — set ANTHROPIC_API_KEY in .env)")
        return

    anna_id = chat_db.get_anna_user_id()
    if anna_id is None:
        return

    # Pull the last N turns for context.
    msgs = chat_db.list_messages(conv_id, limit=HISTORY_LIMIT)
    history = _format_history(viewer_id, anna_id, msgs)
    if not history or history[-1]["role"] != "user":
        # Anna only replies after a user message lands.
        return

    sys_prompt = _SYSTEM_PROMPT.format(
        user_first_name=viewer.get("first_name") or "team",
        user_role=viewer.get("user_role") or "staff",
        today=datetime.now().strftime("%A, %B %d, %Y"),
        staging_summary=_build_staging_summary(),
    )

    try:
        resp = await asyncio.to_thread(
            lambda: client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=sys_prompt,
                messages=history,
            )
        )
    except Exception as e:
        _post_anna_message(conv_id, viewer_id, viewer,
                           f"(Anna hit an error: {type(e).__name__}: {e})")
        return

    text = "".join(
        block.text for block in resp.content if getattr(block, "type", "") == "text"
    ).strip() or "(Anna had nothing to say.)"
    _post_anna_message(conv_id, viewer_id, viewer, text)


def _post_anna_message(conv_id: int, viewer_id: int, viewer: dict, body: str) -> None:
    """Persist Anna's reply and fan out via SSE so the user sees it."""
    anna_id = chat_db.get_anna_user_id()
    if anna_id is None:
        return
    try:
        msg = chat_db.insert_message(conv_id, anna_id, body)
    except Exception:
        return
    sender = {"id": anna_id, "display_name": "Anna"}
    recipients = chat_db.participant_ids(conv_id)
    bus.publish(recipients, "message", {**msg, "sender": sender})

    # Notification to the human side only (Anna doesn't need pings).
    others = [uid for uid in recipients if uid != anna_id]
    for uid in others:
        note = chat_db.insert_notification(
            user_id=uid,
            kind="chat_message",
            title="Anna",
            body=msg["body"][:140],
            data={"conversation_id": conv_id, "message_id": msg["id"]},
        )
        bus.publish([uid], "notification", note)
