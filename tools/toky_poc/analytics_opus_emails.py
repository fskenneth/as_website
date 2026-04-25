"""
Run Claude Opus over the email_extracts corpus to surface sales patterns,
quote→close behavior, objection themes, response-time signals, and
recurring customer-service issues across email.

Mirrors analytics_opus.py (call side). Reads from data/email.db on the
host where email_extract.py wrote — designed to run on DO.

Output: tools/toky_poc/out/email_analytics_report.md
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

ROOT = Path("/var/www/as_website") if Path("/var/www/as_website/data/email.db").exists() else Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUT = Path(__file__).resolve().parent / "out"
DB = ROOT / "data" / "email.db"
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY missing", file=sys.stderr); sys.exit(2)

# Classifications worth analyzing — drop notification noise + internal team chatter
HIGH_SIGNAL = {
    "customer_inquiry",
    "quote_sent",
    "quote_followup",
    "scheduling",
    "customer_service",
}
# Vendor/3rd-party included in a separate (smaller) section so they don't dilute sales analysis.
INCLUDE_VENDOR = True

# Body excerpt budget per email (chars). Keeps the prompt bounded.
BODY_CHARS_PER_EMAIL = 2200
# Total transcript-style budget across all emails. ~1.6M chars ≈ 400k tokens — comfortable inside 1M context.
CORPUS_BUDGET_CHARS = 1_600_000


def load_rows(conn) -> list[dict]:
    rows = conn.execute(
        """
        SELECT
            ee.email_id, ee.classification, ee.confidence,
            ee.customer_name, ee.customer_email, ee.customer_phone,
            ee.property_address, ee.intent, ee.outcome, ee.quote_amount,
            ee.objections_json, ee.key_facts_json, ee.extract_json,
            e.from_addr, e.to_addrs, e.subject, e.date_utc, e.body_text, e.body_html
        FROM email_extracts ee
        JOIN emails e ON e.id = ee.email_id
        WHERE ee.classification IN ({})
        ORDER BY e.date_utc DESC
        """.format(",".join("?" for _ in HIGH_SIGNAL | ({"vendor_or_3rd_party"} if INCLUDE_VENDOR else set()))),
        tuple(HIGH_SIGNAL | ({"vendor_or_3rd_party"} if INCLUDE_VENDOR else set())),
    ).fetchall()
    return [dict(r) for r in rows]


def html_to_text(html: str) -> str:
    if not html:
        return ""
    import re
    out = re.sub(r"<[^>]+>", " ", html)
    out = re.sub(r"\s+", " ", out)
    return out


def fmt_email(r: dict) -> str:
    body = (r.get("body_text") or "").strip()
    if not body:
        body = html_to_text(r.get("body_html") or "")
    body = body[:BODY_CHARS_PER_EMAIL]

    extract = {}
    try:
        extract = json.loads(r.get("extract_json") or "{}")
    except Exception:
        pass

    summary = extract.get("summary", "") or ""
    key_facts = extract.get("key_facts") or []
    objections = []
    try:
        objections = json.loads(r.get("objections_json") or "[]")
    except Exception:
        pass

    line = (
        f"## email {r['email_id']}  cls={r['classification']}  conf={r.get('confidence')}\n"
        f"  date: {r.get('date_utc')}\n"
        f"  from: {r.get('from_addr')}\n"
        f"  to:   {r.get('to_addrs')}\n"
        f"  subject: {r.get('subject')}\n"
    )
    if r.get("customer_name") or r.get("customer_email"):
        line += f"  customer: {r.get('customer_name','?')}  {r.get('customer_email','')}\n"
    if r.get("property_address"):
        line += f"  property: {r['property_address']}\n"
    if r.get("intent"):
        line += f"  intent: {r['intent']}\n"
    if r.get("outcome"):
        line += f"  outcome: {r['outcome']}\n"
    if r.get("quote_amount"):
        line += f"  quote_amount: {r['quote_amount']}\n"
    if summary:
        line += f"  summary: {summary}\n"
    if isinstance(key_facts, list) and key_facts:
        line += "  key_facts:\n" + "".join(f"    - {k}\n" for k in key_facts[:6])
    if objections:
        line += f"  objections: {objections}\n"
    line += "  body:\n    " + body.replace("\n", "\n    ")
    return line


def main() -> int:
    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr); return 2

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    rows = load_rows(conn)
    conn.close()
    print(f"loaded {len(rows)} email_extracts (high-signal classifications)")

    bundle: list[str] = []
    used = 0
    dropped = 0
    for r in rows:
        block = fmt_email(r)
        if used + len(block) > CORPUS_BUDGET_CHARS:
            dropped += 1
            continue
        bundle.append(block)
        used += len(block)
    print(f"corpus: {len(bundle)} emails, {used} chars (~{used//4} tokens), dropped {dropped} over budget")

    corpus = "\n\n".join(bundle)

    SYSTEM = """You are a sales-ops analyst for Astra Staging (Toronto home staging).
You're given the structured analysis of recent customer-touching emails (inquiries,
quotes, follow-ups, scheduling, customer service, plus some vendor/3rd-party for context).

Produce a thorough, actionable analytics report. Be concrete: quote exact phrases,
cite email_ids, cite numbers. No vague platitudes. No generic advice.

Sections required:

# 1. Pipeline snapshot
- Volume by classification. Inbound vs outbound split (sender @astrastaging.com or not).
- Typical lifecycle: inquiry → quote_sent → quote_followup → scheduling. How many emails per won deal?
- Quote-amount distribution (min / median / max where present).

# 2. Inquiry → quote conversion
- What QUESTIONS in inquiry emails correlate with a quote being sent quickly?
- What customer attributes (referrer mention, property type, urgency phrasing) predict quote_sent?

# 3. Quote follow-up patterns
- How long until follow-up? What language gets a customer to re-engage?
- Quote phrases that close vs phrases that go silent — quote both, with email_ids.

# 4. Objection taxonomy (email-side)
- List distinct objections customers raise in writing, with frequency + 1 representative quote each.
- For each: what reply (if any) recovered the deal?

# 5. Scheduling friction
- What do scheduling emails get stuck on? Date conflicts, access issues, deposit timing?
- Recurring patterns the team should pre-empt in the quote email.

# 6. Customer-service themes
- Top recurring complaints with email_ids and severity.
- Any patterns by property type or season?

# 7. Vendor / 3rd-party noise
- Companies cold-pitching Astra by email. Useful as a do-not-engage register.

# 8. Concrete process recommendations
- 5-8 specific, actionable changes Kenneth should make to email templates, response SLAs,
  or follow-up cadence. Cite specific email_ids that motivate each rec.
  Bad: 'follow up faster'. Good: 'Inquiries that mention a closing date within 14d
  convert 3x; auto-flag those for same-day quote.'

Write in dense, scannable markdown. Expect a savvy business reader who hates fluff."""

    USER = f"Corpus below. Each block starts with '## email <email_id>'.\n\n{corpus}"

    payload = {
        # Sonnet 4.6 with 1M context — Opus tops out at 200k and the email
        # corpus runs ~400k tokens. Sonnet 4.6 is also ~5x cheaper for input.
        "model": "claude-sonnet-4-6",
        "max_tokens": 16000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": USER}],
    }
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "context-1m-2025-08-07",
        "content-type": "application/json",
    }

    print("calling Opus...")
    t0 = time.time()
    with httpx.Client(timeout=900.0) as c:
        r = c.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
    print(f"responded in {time.time()-t0:.1f}s, status={r.status_code}")
    if r.status_code != 200:
        print("ERROR:", r.text[:2000]); return 1

    body = r.json()
    usage = body.get("usage", {})
    in_toks = usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
    out_toks = usage.get("output_tokens", 0)
    in_rate = 6.0 if in_toks > 200_000 else 3.0
    out_rate = 22.50 if in_toks > 200_000 else 15.0
    cost = in_toks / 1_000_000 * in_rate + out_toks / 1_000_000 * out_rate

    text = "\n\n".join(b["text"] for b in body.get("content", []) if b.get("type") == "text")
    path = OUT / "email_analytics_report.md"
    path.write_text(text)
    print(f"wrote {path}  ({len(text)} chars)  tokens: {in_toks} in / {out_toks} out  est cost: ${cost:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
