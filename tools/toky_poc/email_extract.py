"""
Email extraction pipeline. Reads emails from data/email.db, filters
to high-signal messages (inbound + reply threads, exclude obvious noise),
runs Sonnet 4.5 with a structured tool-use schema, writes to
email_extracts table.

Designed to run on DO. Mirrors backfill_500.py concurrency pattern.
"""
import asyncio, json, os, sqlite3, sys, time
from pathlib import Path
import httpx
from dotenv import load_dotenv

ROOT = Path("/var/www/as_website")
load_dotenv(ROOT / ".env")
DB = ROOT / "data" / "email.db"
KEY = os.environ["ANTHROPIC_API_KEY"]
URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5"

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
CONCURRENCY = 3  # respect anthropic rate limits


def ensure_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_extracts (
            email_id INTEGER PRIMARY KEY,
            classification TEXT,
            confidence REAL,
            customer_name TEXT,
            customer_email TEXT,
            customer_phone TEXT,
            property_address TEXT,
            intent TEXT,
            outcome TEXT,
            quote_amount REAL,
            objections_json TEXT,
            key_facts_json TEXT,
            extract_json TEXT,
            sonnet_input_tokens INTEGER,
            sonnet_output_tokens INTEGER,
            extracted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(email_id) REFERENCES emails(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ee_class ON email_extracts(classification)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ee_phone ON email_extracts(customer_phone)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ee_addr ON email_extracts(property_address)")
    conn.commit()


# Senders we never extract (auto-noise)
NOISE_SENDERS = (
    "noreply@dmarc",
    "noreply-dmarc",
    "no-reply.ftb41@zapier",
    "ibanking@ib.rbc",
    "businessprofile-noreply",
    "noreply@toky.co",
    "reviews@reviewmgr",
    "billing-noreply@google.com",
    "noreply@",  # generic catch — last resort
)
NOISE_SUBJECTS = (
    "Pay stub", "Stripe receipt", "DMARC", "[Stripe]", "Daily Toky",
)


def is_high_signal(row) -> bool:
    """Inbound from external OR reply OR mentions astrastaging-relevant keywords."""
    fa = (row["from_addr"] or "").lower()
    subj = (row["subject"] or "").lower()
    for n in NOISE_SENDERS:
        if n in fa:
            return False
    for n in NOISE_SUBJECTS:
        if n.lower() in subj:
            return False
    # Inbound (sender NOT @astrastaging.com) — high signal
    if "@astrastaging.com" not in fa:
        return True
    # Reply threads — high signal even if outbound
    if subj.startswith("re:") or subj.startswith("fwd:"):
        return True
    # Outbound from astrastaging that mentions "quote" — high signal
    if "quote" in subj or "inquiry" in subj or "consultation" in subj:
        return True
    return False


SONNET_TOOL = {
    "name": "record_email_analysis",
    "description": "Record the structured analysis of one email message.",
    "input_schema": {
        "type": "object",
        "properties": {
            "classification": {
                "type": "string",
                "enum": [
                    "customer_inquiry",
                    "quote_sent",
                    "quote_followup",
                    "scheduling",
                    "customer_service",
                    "internal_team",
                    "vendor_or_3rd_party",
                    "automated_notification",
                    "other",
                ],
            },
            "confidence": {"type": "number"},
            "summary": {"type": "string", "description": "1-2 sentence what-happened-in-this-email."},
            "customer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                },
            },
            "property": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "property_type": {"type": "string"},
                },
            },
            "intent": {"type": "string", "description": "What the sender wants: e.g. 'request quote', 'confirm booking', 'reschedule', 'complain', 'ask about availability'."},
            "outcome": {"type": "string", "description": "won|lost|pending|n/a — relative to a sales thread"},
            "quote_amount": {"type": "number", "description": "Dollar amount mentioned in this email if any (no commas, no $)."},
            "objections_raised": {"type": "array", "items": {"type": "string"}},
            "key_facts": {"type": "array", "items": {"type": "string"}, "description": "Bullet-list of concrete facts: dates, amounts, room counts, etc."},
        },
        "required": ["classification", "confidence", "summary"],
    },
}

SONNET_SYSTEM = """You analyze emails for Astra Staging, a Toronto home-staging company. Most emails relate to a sales pipeline: customer inquiry → quote sent → negotiation → booking. Some are internal team coordination, some are automated notifications.

Populate record_email_analysis. Be conservative:
- automated notifications (Stripe receipts, Toky daily digests, DMARC reports) → classification=automated_notification, leave fields empty.
- vendor / 3rd party (recruitment, sales pitches TO Astra) → vendor_or_3rd_party.
- internal team chatter (Aashika to Clara, etc.) → internal_team.
- Otherwise classify as the most specific sales/CS bucket.

Pull customer name + phone + property address whenever they appear in the body or signature. Quote amounts: extract as a plain number (no $).

Be terse — short summaries, 3-6 key_facts max."""


def fetch_signal_emails(conn, limit):
    rows = conn.execute("""
        SELECT id, from_addr, subject, body_text, body_html, date_utc
        FROM emails
        WHERE id NOT IN (SELECT email_id FROM email_extracts)
        ORDER BY id DESC
    """).fetchall()
    out = []
    for r in rows:
        if is_high_signal(r):
            out.append(r)
        if len(out) >= limit:
            break
    return out


def build_prompt(row):
    body = (row["body_text"] or "").strip()
    if not body and row["body_html"]:
        # crude html strip
        import re
        body = re.sub(r"<[^>]+>", " ", row["body_html"] or "")
        body = re.sub(r"\s+", " ", body)
    body = body[:6000]  # cap to keep cost predictable
    return (
        f"From: {row['from_addr']}\n"
        f"Subject: {row['subject']}\n"
        f"Date: {row['date_utc']}\n\n"
        f"{body}"
    )


def process_one_sync(row):
    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.row_factory = sqlite3.Row
    try:
        payload = {
            "model": MODEL,
            "max_tokens": 1024,
            "system": [{"type": "text", "text": SONNET_SYSTEM, "cache_control": {"type": "ephemeral"}}],
            "tools": [SONNET_TOOL],
            "tool_choice": {"type": "tool", "name": "record_email_analysis"},
            "messages": [{"role": "user", "content": build_prompt(row)}],
        }
        headers = {
            "x-api-key": KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        for attempt in range(6):
            r = httpx.post(URL, headers=headers, json=payload, timeout=60.0)
            if r.status_code == 429:
                try:
                    wait = float(r.headers.get("retry-after", "8"))
                except ValueError:
                    wait = 8.0
                time.sleep(max(wait, 5.0 * (attempt + 1)))
                continue
            break
        if r.status_code != 200:
            return {"id": row["id"], "error": f"sonnet {r.status_code}: {r.text[:300]}"}
        body = r.json()
        u = body.get("usage", {})
        for block in body.get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "record_email_analysis":
                d = block["input"]
                cust = d.get("customer") if isinstance(d.get("customer"), dict) else {}
                prop = d.get("property") if isinstance(d.get("property"), dict) else {}
                conn.execute("""
                    INSERT OR REPLACE INTO email_extracts
                    (email_id, classification, confidence, customer_name, customer_email,
                     customer_phone, property_address, intent, outcome, quote_amount,
                     objections_json, key_facts_json, extract_json,
                     sonnet_input_tokens, sonnet_output_tokens)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    row["id"], d.get("classification"), float(d.get("confidence") or 0),
                    cust.get("name"), cust.get("email"), cust.get("phone"),
                    prop.get("address"), d.get("intent"), d.get("outcome"),
                    d.get("quote_amount"),
                    json.dumps(d.get("objections_raised") or []),
                    json.dumps(d.get("key_facts") or []),
                    json.dumps(d),
                    int(u.get("input_tokens") or 0),
                    int(u.get("output_tokens") or 0),
                ))
                conn.commit()
                return {"id": row["id"], "ok": True, "class": d.get("classification"),
                        "in": int(u.get("input_tokens") or 0), "out": int(u.get("output_tokens") or 0)}
        return {"id": row["id"], "error": "no tool_use"}
    finally:
        conn.close()


async def main():
    conn = sqlite3.connect(DB, timeout=30)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    rows = fetch_signal_emails(conn, LIMIT)
    conn.close()
    print(f"high-signal emails to process: {len(rows)}")

    sem = asyncio.Semaphore(CONCURRENCY)
    done = 0
    errs = 0
    in_tot = out_tot = 0
    classes: dict = {}

    async def run(row):
        nonlocal done, errs, in_tot, out_tot
        async with sem:
            res = await asyncio.to_thread(process_one_sync, row)
        done += 1
        if res.get("ok"):
            in_tot += res.get("in", 0)
            out_tot += res.get("out", 0)
            classes[res.get("class", "?")] = classes.get(res.get("class", "?"), 0) + 1
        else:
            errs += 1
        if done % 50 == 0 or done == len(rows):
            cost = in_tot/1_000_000*3.0 + out_tot/1_000_000*15.0
            print(f"  {done}/{len(rows)}  errs={errs}  cost so far ${cost:.2f}")

    t0 = time.time()
    await asyncio.gather(*[run(r) for r in rows])
    cost = in_tot/1_000_000*3.0 + out_tot/1_000_000*15.0
    print(f"\ndone in {time.time()-t0:.0f}s")
    print(f"  classifications: {dict(sorted(classes.items(), key=lambda x: -x[1]))}")
    print(f"  total tokens: {in_tot} in / {out_tot} out  cost: ${cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
