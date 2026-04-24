"""
Toky call-intelligence pipeline.

End-to-end flow per call:
    1. Toky webhook fires → CDR row inserted with status='pending'
    2. Background worker picks it up → downloads mp3 from record_url
    3. Deepgram Nova-3 (multichannel + diarize) → transcript + speakers
    4. Claude Sonnet 4.5 (tool-use) → structured extraction
    5. Derived rows: cs_tasks (if customer_service_issue), staging_project_drafts
    6. Optional Telegram ping when something needs Kenneth's eyes

Keeps the same httpx/REST style as ai_service.py — no SDKs, small surface.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


# ---------------- config ----------------

ROOT = Path(__file__).resolve().parents[2]
TOKY_AUDIO_DIR = ROOT / "data" / "toky_audio"
TOKY_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

TOKY_API_BASE = "https://api.toky.co/v1"
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

DEEPGRAM_PARAMS = {
    "model": "nova-3",
    "language": "en",
    "punctuate": "true",
    "smart_format": "true",
    "diarize": "true",
    "utterances": "true",
    "multichannel": "true",
    "keyterm": "Astra",
}

SONNET_MODEL = "claude-sonnet-4-5"
NOISE_THRESHOLD_S = 4

# Mirrors routes.py._QUOTE_CATALOG — kept as a name list for the Sonnet prompt.
_CATALOG_NAMES = [
    "Sofa", "Accent Chair", "Coffee Table", "End Table", "Console", "Bench",
    "Area Rug", "Lamp", "Cushion", "Throw", "Table Decor", "Wall Art",
    "Formal Dining Set", "Bar Stool", "Casual Dining Set",
    "Queen Bed Frame", "Queen Headboard", "Queen Mattress", "Queen Beddings",
    "King Bed Frame", "King Headboard", "King Mattress", "King Beddings",
    "Double Bed Frame", "Double Headboard", "Double Mattress", "Double Bedding",
    "Night Stand",
    "Single Bed Frame", "Single Headboard", "Single Mattress", "Single Beddings",
    "Desk", "Chair", "Patio Set",
]

_SONNET_SYSTEM = f"""You analyze phone-call transcripts from Astra Staging, a Toronto home-staging company. Toky records stereo; Ch0 = agent, Ch1 = caller. Trust channel labels. Agents include Clara, Claire, Ashika; they self-identify as 'Astra Staging'.

Populate record_call_analysis. Be conservative:
- voicemail/system-message/hang-up → call_type=voicemail_or_failed, empty fields
- someone selling TO Astra → cold_call_inbound, no action items
- damage/complaint → cs_task with severity (low|normal|high|urgent) + callback_number
- sales_signal fields: pull objections ('price is too high', 'need to think'), closing phrases, and classify outcome (won/lost/pending/n/a)
- Only suggest quote lines if furniture was explicitly discussed. Exact names from catalog:
{json.dumps(_CATALOG_NAMES)}
- zoho_match_hint: any address or name the agent used that likely maps to a Staging_Report row.

Do NOT invent prices, dates, or names not in transcript."""


_SONNET_TOOL = {
    "name": "record_call_analysis",
    "description": "Record the structured analysis of a phone call.",
    "input_schema": {
        "type": "object",
        "properties": {
            "call_type": {
                "type": "string",
                "enum": [
                    "sales_new_lead", "sales_follow_up", "scheduling",
                    "customer_service_issue", "cold_call_inbound",
                    "voicemail_or_failed", "other",
                ],
            },
            "confidence": {"type": "number"},
            "summary": {"type": "string"},
            "customer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                },
            },
            "property": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "property_type": {"type": "string"},
                    "rooms_discussed": {"type": "array", "items": {"type": "string"}},
                    "occupancy": {"type": "string"},
                },
            },
            "key_points": {"type": "array", "items": {"type": "string"}},
            "action_items": {"type": "array", "items": {"type": "string"}},
            "suggested_quote_lines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_name": {"type": "string"},
                        "area": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "rationale": {"type": "string"},
                    },
                    "required": ["item_name"],
                },
            },
            "cs_task": {
                "type": ["object", "null"],
                "properties": {
                    "title": {"type": "string"},
                    "severity": {"type": "string"},
                    "description": {"type": "string"},
                    "callback_number": {"type": "string"},
                },
            },
            "zoho_match_hint": {"type": "string"},
            "sales_signal": {
                "type": "object",
                "properties": {
                    "objections_raised": {"type": "array", "items": {"type": "string"}},
                    "closing_phrases_used": {"type": "array", "items": {"type": "string"}},
                    "next_step_committed": {"type": "string"},
                    "outcome": {"type": "string"},
                },
            },
        },
        "required": ["call_type", "confidence", "summary"],
    },
}


class TokyServiceError(RuntimeError):
    """Raised when the Toky pipeline hits an unrecoverable error."""


def _key(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise TokyServiceError(f"{name} not set in environment")
    return v


# ---------------- Toky API ----------------

def fetch_recording_url(callid: str) -> Optional[str]:
    """Resolve a callid to its public mp3 URL via GET /recordings/{callid}.
    Webhook payloads may already include `record_url`; use that first. This
    helper is the fallback + the historical-pull path."""
    headers = {"X-Toky-Key": _key("TOKY_API_KEY"), "Accept": "application/json"}
    try:
        with httpx.Client(timeout=30.0) as c:
            r = c.get(f"{TOKY_API_BASE}/recordings/{callid}", headers=headers)
        if r.status_code != 200:
            logger.warning("toky /recordings/%s -> %s %s", callid, r.status_code, r.text[:200])
            return None
        body = r.json()
        if isinstance(body, dict):
            for k in ("url", "record_url", "recording_url"):
                v = body.get(k)
                if isinstance(v, str) and v.startswith("http"):
                    return v
    except httpx.HTTPError as e:
        logger.warning("toky recordings fetch failed for %s: %s", callid, e)
    return None


def download_recording(callid: str, url: str) -> Optional[Path]:
    """Download the mp3 to data/toky_audio/{callid}.mp3. Skip if cached."""
    dest = TOKY_AUDIO_DIR / f"{callid}.mp3"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    try:
        with httpx.Client(timeout=120.0, follow_redirects=True) as c:
            r = c.get(url)
        if r.status_code != 200:
            logger.warning("download %s -> %s", callid, r.status_code)
            return None
        dest.write_bytes(r.content)
        return dest
    except httpx.HTTPError as e:
        logger.warning("download failed for %s: %s", callid, e)
        return None


# ---------------- Deepgram ----------------

def deepgram_transcribe(mp3_path: Path) -> tuple[str, dict]:
    """Submit mp3 to Deepgram Nova-3 (batch) with multichannel + diarize.
    Returns (human-readable speaker-labeled transcript, raw json)."""
    headers = {
        "Authorization": f"Token {_key('DEEPGRAM_API_KEY')}",
        "Content-Type": "audio/mpeg",
    }
    with httpx.Client(timeout=180.0) as c:
        r = c.post(DEEPGRAM_URL, headers=headers, params=DEEPGRAM_PARAMS,
                   content=mp3_path.read_bytes())
    if r.status_code != 200:
        raise TokyServiceError(f"deepgram {r.status_code}: {r.text[:400]}")
    result = r.json()
    text = _format_deepgram(result)
    return text, result


def _format_deepgram(result: dict) -> str:
    """Render Deepgram utterances as 'Ch{N} Speaker {M}: text' lines."""
    utts = result.get("results", {}).get("utterances", []) or []
    chans = result.get("metadata", {}).get("channels", 1)
    lines: list[str] = []
    if utts:
        for u in utts:
            spk = u.get("speaker")
            ch = u.get("channel")
            lbl = f"Speaker {spk}" if spk is not None else "Speaker ?"
            if ch is not None and chans > 1:
                lbl = f"Ch{ch} Speaker {spk if spk is not None else '?'}"
            lines.append(f"{lbl}: {u.get('transcript','').strip()}")
    else:
        for ci, c in enumerate(result.get("results", {}).get("channels", [])):
            alt = (c.get("alternatives") or [{}])[0]
            lines.append(f"Ch{ci}: {alt.get('transcript','').strip()}")
    return "\n".join(lines)


# ---------------- Claude Sonnet extraction ----------------

def sonnet_extract(transcript: str, cdr_context: dict) -> tuple[dict, dict]:
    """Ask Sonnet to produce record_call_analysis for this transcript.
    Returns (extraction_dict, usage_dict). Raises TokyServiceError on failure."""
    ctx = (
        f"Metadata: direction={cdr_context.get('direction')}  "
        f"duration={cdr_context.get('duration')}s  "
        f"agent={cdr_context.get('agent_id')}  "
        f"from={cdr_context.get('from')}  "
        f"to={cdr_context.get('received_on_number') or cdr_context.get('to_number')}  "
        f"init_dt={cdr_context.get('init_dt') or cdr_context.get('date')}"
    )
    payload = {
        "model": SONNET_MODEL,
        "max_tokens": 2048,
        # Cache the (static, long) system prompt so repeat calls are cheap.
        "system": [
            {"type": "text", "text": _SONNET_SYSTEM, "cache_control": {"type": "ephemeral"}},
        ],
        "tools": [_SONNET_TOOL],
        "tool_choice": {"type": "tool", "name": "record_call_analysis"},
        "messages": [
            {"role": "user", "content": f"{ctx}\n\nTranscript:\n\n{transcript}"},
        ],
    }
    headers = {
        "x-api-key": _key("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # Anthropic 429 happens when we burst — retry with backoff.
    import time
    for attempt in range(6):
        with httpx.Client(timeout=120.0) as c:
            r = c.post(ANTHROPIC_URL, headers=headers, json=payload)
        if r.status_code == 429:
            try:
                wait = float(r.headers.get("retry-after", "8"))
            except ValueError:
                wait = 8.0
            time.sleep(max(wait, 5.0 * (attempt + 1)))
            continue
        break
    if r.status_code != 200:
        raise TokyServiceError(f"sonnet {r.status_code}: {r.text[:400]}")
    body = r.json()
    usage = body.get("usage", {})
    for block in body.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "record_call_analysis":
            return block["input"], usage
    raise TokyServiceError(f"sonnet returned no tool_use block: {body}")


# ---------------- DB helpers ----------------

def ensure_tables(conn: sqlite3.Connection) -> None:
    """Create toky_* tables if they don't exist. Idempotent."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS toky_calls (
            callid TEXT PRIMARY KEY,
            direction TEXT,
            agent_id TEXT,
            from_number TEXT,
            to_number TEXT,
            duration_s INTEGER,
            init_dt TEXT,
            end_dt TEXT,
            record_url TEXT,
            disposition_code TEXT,
            raw_cdr_json TEXT,
            status TEXT DEFAULT 'pending',
            error TEXT,
            received_at TEXT DEFAULT CURRENT_TIMESTAMP,
            processed_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_toky_calls_status ON toky_calls(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_toky_calls_init ON toky_calls(init_dt)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS toky_transcripts (
            callid TEXT PRIMARY KEY,
            transcript_text TEXT,
            deepgram_json TEXT,
            duration_s REAL,
            transcribed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS toky_extracts (
            callid TEXT PRIMARY KEY,
            call_type TEXT,
            confidence REAL,
            summary TEXT,
            extract_json TEXT,
            sonnet_input_tokens INTEGER,
            sonnet_output_tokens INTEGER,
            extracted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_toky_extracts_type ON toky_extracts(call_type)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS toky_cs_tasks (
            id TEXT PRIMARY KEY,
            callid TEXT NOT NULL,
            title TEXT,
            severity TEXT,
            description TEXT,
            callback_number TEXT,
            status TEXT DEFAULT 'open',
            assignee TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            FOREIGN KEY(callid) REFERENCES toky_calls(callid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cs_tasks_status ON toky_cs_tasks(status)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS toky_staging_drafts (
            id TEXT PRIMARY KEY,
            callid TEXT NOT NULL,
            call_type TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            property_address TEXT,
            property_type TEXT,
            rooms_discussed_json TEXT,
            quote_lines_json TEXT,
            zoho_match_hint TEXT,
            next_step TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            FOREIGN KEY(callid) REFERENCES toky_calls(callid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_drafts_status ON toky_staging_drafts(status)")

    conn.commit()


def insert_cdr(conn: sqlite3.Connection, cdr: dict) -> str:
    """Insert a Toky CDR into toky_calls. Returns the callid. Idempotent on
    callid (INSERT OR IGNORE) so webhook retries are safe."""
    callid = cdr.get("callid") or cdr.get("id")
    if not callid:
        raise TokyServiceError("cdr missing callid")
    try:
        duration = int(cdr.get("duration") or 0)
    except (ValueError, TypeError):
        duration = 0
    record_url = (cdr.get("record_url") or cdr.get("recording_url") or "")
    conn.execute("""
        INSERT OR IGNORE INTO toky_calls (
            callid, direction, agent_id, from_number, to_number,
            duration_s, init_dt, end_dt, record_url, disposition_code,
            raw_cdr_json, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        callid, cdr.get("direction"), cdr.get("agent_id"),
        cdr.get("from"), cdr.get("to_number") or cdr.get("received_on_number"),
        duration, cdr.get("init_dt") or cdr.get("date"), cdr.get("end_time"),
        record_url, cdr.get("disposition_code"),
        json.dumps(cdr),
    ))
    conn.commit()
    return callid


def claim_next_pending(conn: sqlite3.Connection) -> Optional[dict]:
    """Atomically claim the next pending call. Returns the CDR-ish row,
    or None if the queue is empty."""
    row = conn.execute(
        "SELECT callid, raw_cdr_json, duration_s, record_url FROM toky_calls "
        "WHERE status = 'pending' ORDER BY received_at ASC LIMIT 1"
    ).fetchone()
    if not row:
        return None
    # Mark as processing so a parallel worker doesn't double-process.
    cur = conn.execute(
        "UPDATE toky_calls SET status = 'processing' "
        "WHERE callid = ? AND status = 'pending'",
        (row[0],),
    )
    conn.commit()
    if cur.rowcount == 0:
        return None  # someone else got it
    try:
        cdr = json.loads(row[1] or "{}")
    except json.JSONDecodeError:
        cdr = {}
    cdr["callid"] = row[0]
    cdr.setdefault("duration", row[2])
    cdr.setdefault("record_url", row[3])
    return cdr


def mark_done(conn: sqlite3.Connection, callid: str, status: str = "done", error: Optional[str] = None) -> None:
    conn.execute(
        "UPDATE toky_calls SET status = ?, error = ?, processed_at = ? WHERE callid = ?",
        (status, error, datetime.utcnow().isoformat(), callid),
    )
    conn.commit()


# ---------------- end-to-end per-call processing ----------------

def process_call(conn: sqlite3.Connection, cdr: dict) -> dict:
    """Download → transcribe → extract → persist derived rows.
    Returns a small summary dict (for logging/ping)."""
    callid: str = cdr["callid"]
    try:
        duration = int(cdr.get("duration") or 0)
    except (ValueError, TypeError):
        duration = 0

    # Short noise → mark done without burning Deepgram/Sonnet.
    if duration < NOISE_THRESHOLD_S:
        conn.execute("""
            INSERT OR REPLACE INTO toky_extracts
                (callid, call_type, confidence, summary, extract_json)
            VALUES (?, 'voicemail_or_failed', 1.0, 'Too short to transcribe (<4s).', ?)
        """, (callid, json.dumps({"auto_skipped": "noise"})))
        mark_done(conn, callid, status="done")
        return {"callid": callid, "call_type": "voicemail_or_failed", "skipped": True}

    # 1. Resolve recording URL + download
    url = cdr.get("record_url") or fetch_recording_url(callid)
    if not url:
        mark_done(conn, callid, status="no_recording", error="recording url not available")
        return {"callid": callid, "error": "no_recording"}
    mp3 = download_recording(callid, url)
    if not mp3:
        mark_done(conn, callid, status="download_err", error="recording download failed")
        return {"callid": callid, "error": "download_err"}

    # 2. Deepgram
    transcript_text, dg_json = deepgram_transcribe(mp3)
    dg_duration = dg_json.get("metadata", {}).get("duration", duration)
    conn.execute("""
        INSERT OR REPLACE INTO toky_transcripts
            (callid, transcript_text, deepgram_json, duration_s)
        VALUES (?, ?, ?, ?)
    """, (callid, transcript_text, json.dumps(dg_json), float(dg_duration or 0)))

    # 3. Sonnet extraction
    extract, usage = sonnet_extract(transcript_text, cdr)
    conn.execute("""
        INSERT OR REPLACE INTO toky_extracts
            (callid, call_type, confidence, summary, extract_json,
             sonnet_input_tokens, sonnet_output_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        callid, extract.get("call_type"), float(extract.get("confidence") or 0),
        extract.get("summary"), json.dumps(extract),
        int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0),
    ))

    # 4. Derived rows
    _maybe_insert_cs_task(conn, callid, extract)
    _maybe_insert_staging_draft(conn, callid, extract)

    mark_done(conn, callid, status="done")
    return {
        "callid": callid,
        "call_type": extract.get("call_type"),
        "confidence": extract.get("confidence"),
        "cs_task": bool(_coerce_dict(extract.get("cs_task"))),
        "summary": extract.get("summary"),
    }


def _coerce_dict(v: Any) -> Optional[dict]:
    return v if isinstance(v, dict) else None


def _maybe_insert_cs_task(conn: sqlite3.Connection, callid: str, extract: dict) -> None:
    cs = _coerce_dict(extract.get("cs_task"))
    if not cs or not cs.get("title"):
        return
    conn.execute("""
        INSERT INTO toky_cs_tasks
            (id, callid, title, severity, description, callback_number, status)
        VALUES (?, ?, ?, ?, ?, ?, 'open')
    """, (
        f"cs-{uuid.uuid4().hex}", callid,
        cs.get("title"), cs.get("severity"), cs.get("description"),
        cs.get("callback_number"),
    ))


def _maybe_insert_staging_draft(conn: sqlite3.Connection, callid: str, extract: dict) -> None:
    call_type = extract.get("call_type")
    # Only create drafts for the kinds of calls we might actually want to action.
    if call_type not in ("sales_new_lead", "sales_follow_up", "scheduling", "other"):
        return
    customer = _coerce_dict(extract.get("customer")) or {}
    property_ = _coerce_dict(extract.get("property")) or {}
    sales = _coerce_dict(extract.get("sales_signal")) or {}
    conn.execute("""
        INSERT INTO toky_staging_drafts (
            id, callid, call_type,
            customer_name, customer_phone, customer_email,
            property_address, property_type,
            rooms_discussed_json, quote_lines_json,
            zoho_match_hint, next_step, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft')
    """, (
        f"sd-{uuid.uuid4().hex}", callid, call_type,
        customer.get("name") or None, customer.get("phone") or None, customer.get("email") or None,
        property_.get("address") or None, property_.get("property_type") or None,
        json.dumps(property_.get("rooms_discussed") or []),
        json.dumps(extract.get("suggested_quote_lines") or []),
        extract.get("zoho_match_hint") or None,
        sales.get("next_step_committed") or None,
    ))
