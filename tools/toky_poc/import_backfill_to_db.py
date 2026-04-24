"""
Import the POC backfill output (tools/toky_poc/out/*.extract.json + matching
dg.txt + mp3 metadata) into the live server DB so /toky_call_intake shows
all 411 processed calls, not just the ones that came in via webhook.

Idempotent: rerunning only inserts rows that aren't already there.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path("/Users/kennethjin/Desktop/development/as_website")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import httpx
import uuid

OUT = ROOT / "tools" / "toky_poc" / "out"
DB = ROOT / "data" / "zoho_sync.db"
TOKY_KEY = (ROOT / ".env").read_text().split("TOKY_API_KEY=")[1].split("\n")[0].strip()

# CDR metadata from the backfill is in cdrs.json (dumped by fetch script)
CDRS = json.loads((OUT / "cdrs.json").read_text()) if (OUT / "cdrs.json").exists() else []
cdr_by_id = {c.get("callid"): c for c in CDRS if c.get("callid")}

# The backfill script's log.jsonl has one entry per call processed by the
# newer run (post-fixes). Read it for authoritative status.
log_statuses = {}
log_path = OUT / "backfill_log.jsonl"
if log_path.exists():
    for line in log_path.read_text().splitlines():
        try:
            e = json.loads(line)
            log_statuses[e["callid"]] = e
        except Exception:
            pass

# For calls not in cdr_by_id (older POC runs), fetch fresh CDR from Toky
# just to fill columns. Skip lazily — most of our 411 are covered.


def fetch_cdr_fallback(callid: str) -> dict | None:
    """If we don't have the CDR locally, try Toky /cdrs (limited)."""
    try:
        with httpx.Client(timeout=15.0) as c:
            r = c.get(
                "https://api.toky.co/v1/cdrs",
                params={"callid": callid, "limit": 1},
                headers={"X-Toky-Key": TOKY_KEY},
            )
        if r.status_code == 200:
            results = r.json().get("results") or []
            if results:
                return results[0]
    except Exception:
        pass
    return None


def main() -> int:
    conn = sqlite3.connect(DB)

    extracts = sorted(OUT.glob("*.extract.json"))
    print(f"Importing {len(extracts)} extracts...")

    inserted_calls = 0
    updated_calls = 0
    inserted_extracts = 0
    inserted_transcripts = 0
    inserted_cs = 0
    inserted_drafts = 0

    for p in extracts:
        callid = p.stem.replace(".extract", "")
        try:
            extract = json.loads(p.read_text())
        except Exception as e:
            print(f"  skip {callid}: bad JSON ({e})")
            continue

        # Skip the synthetic "tailscale-funnel-test" artifact if present
        if callid.startswith("tailscale-funnel"):
            continue

        cdr = cdr_by_id.get(callid) or {}

        # toky_calls — upsert
        existing = conn.execute("SELECT status FROM toky_calls WHERE callid = ?", (callid,)).fetchone()
        if not existing:
            try:
                duration = int(cdr.get("duration") or 0)
            except (ValueError, TypeError):
                duration = 0
            conn.execute("""
                INSERT INTO toky_calls
                    (callid, direction, agent_id, from_number, to_number,
                     duration_s, init_dt, record_url, disposition_code,
                     raw_cdr_json, status, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'done', CURRENT_TIMESTAMP)
            """, (
                callid, cdr.get("direction"), cdr.get("agent_id"),
                cdr.get("from"), cdr.get("to_number") or cdr.get("received_on_number"),
                duration, cdr.get("init_dt"),
                cdr.get("record_url") or "",
                cdr.get("disposition_code"),
                json.dumps(cdr),
            ))
            inserted_calls += 1
        else:
            # Ensure status=done for anything we have extracts for
            if existing[0] != "done":
                conn.execute(
                    "UPDATE toky_calls SET status='done' WHERE callid = ?", (callid,)
                )
                updated_calls += 1

        # toky_extracts
        has_extract = conn.execute("SELECT 1 FROM toky_extracts WHERE callid = ?", (callid,)).fetchone()
        if not has_extract:
            conn.execute("""
                INSERT INTO toky_extracts
                    (callid, call_type, confidence, summary, extract_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                callid,
                extract.get("call_type"),
                float(extract.get("confidence") or 0),
                extract.get("summary"),
                json.dumps(extract),
            ))
            inserted_extracts += 1

        # toky_transcripts
        dg_path = OUT / f"{callid}.dg.txt"
        dg_json_path = OUT / f"{callid}.dg.json"
        if dg_path.exists():
            has_t = conn.execute("SELECT 1 FROM toky_transcripts WHERE callid = ?", (callid,)).fetchone()
            if not has_t:
                dg_json_body = dg_json_path.read_text() if dg_json_path.exists() else ""
                conn.execute("""
                    INSERT INTO toky_transcripts
                        (callid, transcript_text, deepgram_json, duration_s)
                    VALUES (?, ?, ?, ?)
                """, (callid, dg_path.read_text(), dg_json_body, 0.0))
                inserted_transcripts += 1

        # toky_cs_tasks — only if extract has a cs_task
        cs = extract.get("cs_task") if isinstance(extract.get("cs_task"), dict) else None
        if cs and cs.get("title"):
            # dedupe: skip if we already have an open/resolved row for this callid with same title
            dup = conn.execute(
                "SELECT 1 FROM toky_cs_tasks WHERE callid = ? AND title = ?",
                (callid, cs.get("title")),
            ).fetchone()
            if not dup:
                conn.execute("""
                    INSERT INTO toky_cs_tasks
                        (id, callid, title, severity, description, callback_number, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'open')
                """, (
                    f"cs-{uuid.uuid4().hex}", callid,
                    cs.get("title"), cs.get("severity"), cs.get("description"),
                    cs.get("callback_number"),
                ))
                inserted_cs += 1

        # toky_staging_drafts — for sales/scheduling/other call types
        call_type = extract.get("call_type")
        if call_type in ("sales_new_lead", "sales_follow_up", "scheduling", "other"):
            dup_draft = conn.execute(
                "SELECT 1 FROM toky_staging_drafts WHERE callid = ?", (callid,),
            ).fetchone()
            if not dup_draft:
                customer = extract.get("customer") if isinstance(extract.get("customer"), dict) else {}
                property_ = extract.get("property") if isinstance(extract.get("property"), dict) else {}
                sales = extract.get("sales_signal") if isinstance(extract.get("sales_signal"), dict) else {}
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
                    customer.get("name") or None,
                    customer.get("phone") or None,
                    customer.get("email") or None,
                    property_.get("address") or None,
                    property_.get("property_type") or None,
                    json.dumps(property_.get("rooms_discussed") or []),
                    json.dumps(extract.get("suggested_quote_lines") or []),
                    extract.get("zoho_match_hint") or None,
                    sales.get("next_step_committed") or None,
                ))
                inserted_drafts += 1

    conn.commit()
    conn.close()

    print(f"  inserted toky_calls:      {inserted_calls} (updated: {updated_calls})")
    print(f"  inserted toky_extracts:   {inserted_extracts}")
    print(f"  inserted toky_transcripts: {inserted_transcripts}")
    print(f"  inserted toky_cs_tasks:   {inserted_cs}")
    print(f"  inserted toky_staging_drafts: {inserted_drafts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
