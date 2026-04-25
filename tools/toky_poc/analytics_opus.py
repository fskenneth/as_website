"""
Workstream A: run Claude Opus over the full Toky corpus to extract
sales patterns, objection taxonomy, agent performance, and CS themes.

Strategy: feed Opus
  - all structured extracts (cheap, structured, dense)
  - full Deepgram transcripts of high-signal subset (sales + scheduling + CS),
    budgeted by char count so the prompt fits the 1M context window
  - NO voicemails or cold calls (low signal, would dilute)

Source of truth: data/zoho_sync.db tables toky_calls/toky_extracts/toky_transcripts.
Falls back to per-callid files in out/ if the DB lookup yields no transcript
(legacy mac-local extracts have files but no DB rows).

Output: tools/toky_poc/out/analytics_report.md
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path("/var/www/as_website") if Path("/var/www/as_website/data/zoho_sync.db").exists() else Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUT = Path(__file__).resolve().parent / "out"
DB = ROOT / "data" / "zoho_sync.db"
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY missing", file=sys.stderr); sys.exit(2)

# Load every call that has an extract. Joins to transcripts so we can attach
# the diarized text to high-signal subsets later.
extracts: list[dict] = []
if DB.exists():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT c.callid, c.direction, c.duration_s, c.agent_id, c.init_dt,
               e.call_type, e.confidence, e.summary, e.extract_json,
               t.transcript_text
        FROM toky_calls c
        JOIN toky_extracts e ON e.callid = c.callid
        LEFT JOIN toky_transcripts t ON t.callid = c.callid
    """).fetchall()
    conn.close()
    for r in rows:
        try:
            d = json.loads(r["extract_json"] or "{}")
        except Exception:
            d = {}
        # Denormalized columns win over extract_json if both present.
        d["_callid"] = r["callid"]
        d["_agent_id"] = r["agent_id"]
        d["_transcript"] = r["transcript_text"]
        d.setdefault("call_type", r["call_type"])
        d.setdefault("confidence", r["confidence"])
        d.setdefault("summary", r["summary"])
        extracts.append(d)

# Also pick up any legacy file-based extracts not yet in the DB (older mac
# run wrote .extract.json but no DB row). Skip duplicates by callid.
seen_ids = {e["_callid"] for e in extracts}
for p in sorted(OUT.glob("*.extract.json")):
    cid = p.stem.replace(".extract", "")
    if cid in seen_ids:
        continue
    try:
        d = json.loads(p.read_text())
        d["_callid"] = cid
        d["_agent_id"] = None
        dg = OUT / f"{cid}.dg.txt"
        d["_transcript"] = dg.read_text() if dg.exists() else None
        extracts.append(d)
    except Exception:
        pass

# High-signal types worth sending the transcript for
HIGH_SIGNAL = {"sales_new_lead", "sales_follow_up", "scheduling", "customer_service_issue"}

# Drop voicemail + cold_call + failed from the corpus entirely — they add
# noise without signal. Keep 'other' because Sonnet sometimes puts real
# calls there.
INCLUDE = HIGH_SIGNAL | {"other"}

bundle_rows: list[tuple[str, str, str, str | None]] = []
for e in extracts:
    ct = e.get("call_type", "other") or "other"
    if ct not in INCLUDE:
        continue
    callid = e["_callid"]
    line = f"## call {callid}  type={ct}  conf={e.get('confidence')}"
    if e.get("_agent_id"):
        line += f"  agent={e['_agent_id']}"
    line += f"\n  summary: {e.get('summary','')}"
    customer = e.get("customer") if isinstance(e.get("customer"), dict) else {}
    if customer.get("name") or customer.get("phone"):
        line += f"\n  customer: {customer.get('name','?')}  {customer.get('phone','')}"
    property_ = e.get("property") if isinstance(e.get("property"), dict) else {}
    if property_.get("address"):
        line += f"\n  property: {property_.get('address')}  type={property_.get('property_type','?')}  rooms={property_.get('rooms_discussed',[])}"
    kp = e.get("key_points") or []
    if isinstance(kp, list) and kp:
        line += "\n  key_points:"
        for k in kp[:6]:
            line += f"\n    - {k}"
    sales = e.get("sales_signal") if isinstance(e.get("sales_signal"), dict) else {}
    if sales.get("objections_raised") or sales.get("closing_phrases_used") or sales.get("outcome"):
        line += f"\n  sales_signal: outcome={sales.get('outcome','?')}  next={sales.get('next_step_committed','')}"
        if sales.get("objections_raised"):
            line += f"\n    objections: {sales['objections_raised']}"
        if sales.get("closing_phrases_used"):
            line += f"\n    closing: {sales['closing_phrases_used']}"
    cs = e.get("cs_task") if isinstance(e.get("cs_task"), dict) else None
    if cs:
        line += f"\n  cs_task: {cs.get('severity','?')} - {cs.get('title','')}"

    bundle_rows.append((ct, callid, line, e.get("_transcript")))

# Attach transcripts only to high-signal calls, prioritizing CS + new_lead + follow_up.
# Budget chars so total prompt comfortably fits 1M context.
TRANSCRIPT_PRIORITY = [
    "customer_service_issue",
    "sales_new_lead",
    "sales_follow_up",
]
TRANSCRIPT_BUDGET_CHARS = 1_400_000  # ~350k tokens of transcripts; full prompt stays under 1M
used_chars = 0
for pri in TRANSCRIPT_PRIORITY:
    for i, (ct, callid, line, txt) in enumerate(bundle_rows):
        if ct != pri or not txt:
            continue
        if used_chars + len(txt) > TRANSCRIPT_BUDGET_CHARS:
            continue
        used_chars += len(txt)
        bundle_rows[i] = (ct, callid, line + "\n  transcript: " + "\n    " + txt.replace("\n", "\n    "), None)

corpus = "\n\n".join(row[2] for row in bundle_rows)
print(f"Loaded {len(extracts)} extracts ({len(bundle_rows)} after INCLUDE filter)")
print(f"Corpus size: {len(corpus)} chars (~{len(corpus)//4} tokens), transcript chars used: {used_chars}")

SYSTEM = """You are a sales-ops analyst for Astra Staging (Toronto home staging).
You're given the structured analysis of ~400 recent phone calls plus full
diarized transcripts for the high-signal subset (sales + scheduling + CS).

Produce a thorough, actionable analytics report. Be concrete: quote exact
phrases, call callids by their short prefix (first 8 chars), cite numbers.
No vague platitudes. No generic advice.

Sections required:

# 1. Pipeline snapshot
- Volume by call type. Direction split. Typical agent (Clara/Claire/Ashika) workload.
- % of inbound that's actionable vs noise (voicemail + cold + failed).

# 2. Sales patterns that close
- What OPENING phrases (agent's first 1-2 turns) correlate with a good call flow?
- What CLOSING phrases commit the customer to a next step?
- What CALL LENGTHS correlate with conversion (won outcome vs pending/lost)?
- What QUESTIONS from the agent elicit the most property-specific detail?

# 3. Objection taxonomy
- List the distinct customer objections with frequency counts and 1 representative quote each.
- For each objection: what response (if any) worked best?

# 4. Agent scorecard (by agent_id)
- Call volume, avg duration, % leading to committed next step.
- Distinctive strengths / weaknesses per agent, with one quoted example.
- If one agent has a pattern others don't (good or bad), call it out.

# 5. Customer-service theme clustering
- Group the CS issues. What are the top 3 recurring complaints?
- Any patterns in severity / callback urgency?

# 6. Cold-call vendor spam
- List the companies/people cold-calling Astra to sell services.
  Useful as a block-list or 'do not engage' register.

# 7. Concrete CRM / process recommendations
- 3-6 specific changes Kenneth should implement based on the data.
  Examples of good rec: 'Train agents to ask "when were you hoping to list?" at minute 1 — 80% of the won calls had this early' or 'Add a checklist item for HVAC-damage incidents; 3 separate calls reference moving-damage claims'.
  Bad rec: 'improve customer service' / 'follow up more'.

Write in dense, scannable markdown. Expect a savvy business reader who hates fluff."""

USER = f"Corpus below. Each call block starts with '## call <callid>'.\n\n{corpus}"

payload = {
    # Sonnet 4.6 with 1M context — Opus tops out at 200k and the corpus
    # is ~575k tokens. Sonnet 4.6 is also ~5x cheaper for input.
    "model": "claude-sonnet-4-6",
    "max_tokens": 16000,
    "system": SYSTEM,
    "messages": [{"role": "user", "content": USER}],
}

headers = {
    "x-api-key": ANTHROPIC_KEY,
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "context-1m-2025-08-07",  # enable 1M context if corpus grows
    "content-type": "application/json",
}

print("calling Opus...")
t0 = time.time()
with httpx.Client(timeout=600.0) as c:
    r = c.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
print(f"responded in {time.time()-t0:.1f}s, status={r.status_code}")

if r.status_code != 200:
    print("ERROR:", r.text[:2000])
    sys.exit(1)

body = r.json()
usage = body.get("usage", {})
report_parts = [blk["text"] for blk in body.get("content", []) if blk.get("type") == "text"]
report = "\n\n".join(report_parts)

# Opus pricing: check actual billing — recent public rate is ~$15/$75 per M.
in_toks = usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
out_toks = usage.get("output_tokens", 0)
in_rate = 6.0 if in_toks > 200_000 else 3.0
out_rate = 22.50 if in_toks > 200_000 else 15.0
cost = in_toks / 1_000_000 * in_rate + out_toks / 1_000_000 * out_rate

report_path = OUT / "analytics_report.md"
report_path.write_text(report)
print(f"report: {report_path}  ({len(report)} chars)")
print(f"tokens: {in_toks} in, {out_toks} out  est cost: ${cost:.2f}")
