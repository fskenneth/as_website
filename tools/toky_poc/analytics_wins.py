"""Run Sonnet 4.6 over just the win-cohort calls (n=~185 after backfill
completed). Reuses the corpus-builder from analytics.py but
filters to callids in wins_mapping.json."""
import json, os, sqlite3, sys, time
from pathlib import Path
import httpx
from dotenv import load_dotenv
ROOT = Path("/var/www/as_website")
load_dotenv(ROOT / ".env")
OUT = ROOT / "tools" / "toky_poc" / "out"

mapping = json.loads((OUT / "wins_mapping.json").read_text())
all_win_callids = set()
for cids in mapping["matches"].values():
    all_win_callids.update(cids)
# Also combine with any new_calls in mapping
all_win_callids.update(mapping.get("new_calls", []))
print(f"targeting {len(all_win_callids)} win-cohort calls")

db = sqlite3.connect(str(ROOT / "data" / "zoho_sync.db"))
db.row_factory = sqlite3.Row

# Pull CDR + extract + transcript for each win callid
rows = []
for cid in all_win_callids:
    r = db.execute("""
        SELECT c.callid, c.direction, c.duration_s, c.agent_id, c.init_dt, c.from_number,
               e.call_type, e.confidence, e.summary, e.extract_json,
               t.transcript_text
        FROM toky_calls c
        LEFT JOIN toky_extracts e ON e.callid = c.callid
        LEFT JOIN toky_transcripts t ON t.callid = c.callid
        WHERE c.callid = ?
    """, (cid,)).fetchone()
    if r and r["call_type"]:
        rows.append(dict(r))
print(f"available with extract: {len(rows)}")

HIGH_SIGNAL = {"sales_new_lead","sales_follow_up","scheduling","customer_service_issue"}
rows = [r for r in rows if r["call_type"] in HIGH_SIGNAL]
print(f"after HIGH_SIGNAL filter: {len(rows)}")

# Build corpus
def fmt_call(r):
    try:
        e = json.loads(r["extract_json"] or "{}")
    except: e = {}
    line = f"## call {r['callid']}  type={r['call_type']}  dur={r['duration_s']}s  agent={r['agent_id']}  dt={r['init_dt']}"
    line += f"\n  summary: {r.get('summary','')}"
    cust = e.get("customer") if isinstance(e.get("customer"), dict) else {}
    prop = e.get("property") if isinstance(e.get("property"), dict) else {}
    if cust.get("name") or cust.get("phone"):
        line += f"\n  customer: {cust.get('name','?')} {cust.get('phone','')}"
    if prop.get("address"):
        line += f"\n  property: {prop.get('address')}"
    sales = e.get("sales_signal") if isinstance(e.get("sales_signal"), dict) else {}
    if sales:
        line += f"\n  outcome: {sales.get('outcome')}  next: {sales.get('next_step_committed','')}"
        if sales.get("objections_raised"):
            line += f"\n  objections: {sales['objections_raised']}"
        if sales.get("closing_phrases_used"):
            line += f"\n  closing: {sales['closing_phrases_used']}"
    kp = e.get("key_points") or []
    if kp:
        line += "\n  key_points:" + "".join(f"\n    - {k}" for k in kp[:6])
    return line, r["transcript_text"]

# Structured summary for every call, full transcript for every call (n~185 fits 1M)
bundle = []
char_budget = 480_000  # ~175k tokens, leaves room for system prompt + response
used = 0
for r in rows:
    line, tx = fmt_call(r)
    if tx:
        line += "\n  transcript:\n    " + (tx or "").replace("\n", "\n    ")
    if used + len(line) > char_budget:
        # Drop transcript for subsequent calls to stay under budget
        line, _ = fmt_call(r)
    used += len(line)
    bundle.append(line)

corpus = "\n\n".join(bundle)
print(f"corpus: {len(corpus)} chars (~{len(corpus)//4} tokens)")

SYSTEM = """You are a sales-ops analyst. You are given ONLY the calls that resulted in WON deals (paid deposit, scheduled staging) for Astra Staging.

Extract ACTIONABLE patterns a sales manager can coach to:

# 1. Opening that works (agent first 1-3 turns)
Quote exact phrases. Identify any opening shared across >=5 won calls.

# 2. Closing moves that commit (agent)
- Exact phrases that secured the deposit / next step
- Which closes work with which objections?

# 3. Deposit-capture moments
- When in the call (minute X) does the deposit commitment typically land?
- What does the agent say RIGHT BEFORE the customer commits?

# 4. Referral handling
- How do agents leverage the referrer's name?
- Does mentioning the referral change objection rate?

# 5. Property size / quote range per property type
- Typical quote: condo / townhouse / house
- Any discount patterns

# 6. Agent by agent — Aashika vs Clara wins
- Call volume + avg duration + typical outcome notes
- Distinctive strengths backed by quotes

# 7. Coaching recommendations — 5 concrete script-level changes

Dense markdown, no fluff. Quote callid prefixes (first 8 chars)."""

USER = f"Corpus ({len(rows)} won calls):\n\n{corpus}"

payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 16000,
    "system": SYSTEM,
    "messages": [{"role": "user", "content": USER}],
}
headers = {
    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

print("calling Sonnet 4.6...")
t0 = time.time()
with httpx.Client(timeout=600.0) as c:
    r = c.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
print(f"status {r.status_code} in {time.time()-t0:.0f}s")
if r.status_code != 200:
    print(r.text[:2000]); sys.exit(1)

body = r.json()
u = body.get("usage", {})
in_tok = u.get("input_tokens",0) + u.get("cache_read_input_tokens",0) + u.get("cache_creation_input_tokens",0)
out_tok = u.get("output_tokens",0)
cost = in_tok/1_000_000*15.0 + out_tok/1_000_000*75.0

text = "\n\n".join(b["text"] for b in body.get("content",[]) if b.get("type")=="text")
path = OUT / "wins_only_analytics.md"
path.write_text(text)
print(f"wrote {path}  {len(text)} chars  tokens: {in_tok} in / {out_tok} out  cost: ${cost:.2f}")
