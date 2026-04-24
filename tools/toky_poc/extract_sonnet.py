"""
Run Claude Sonnet 4.6 over each Deepgram transcript with a structured tool-use
schema that captures classification + extraction for the Toky flow.

Writes tools/toky_poc/out/*.extract.json and prints a compact summary.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUT = Path(__file__).resolve().parent / "out"
KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
if not KEY:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(2)

# Pricing catalog mirrors as_webapp/as_portal_api/routes.py _QUOTE_CATALOG
CATALOG = [
    ("Sofa", 250), ("Accent Chair", 100), ("Coffee Table", 100),
    ("End Table", 50), ("Console", 75), ("Bench", 65),
    ("Area Rug", 80), ("Lamp", 40), ("Cushion", 15),
    ("Throw", 18), ("Table Decor", 10), ("Wall Art", 40),
    ("Formal Dining Set", 400), ("Bar Stool", 40),
    ("Casual Dining Set", 250), ("Queen Bed Frame", 20),
    ("Queen Headboard", 90), ("Queen Mattress", 50),
    ("Queen Beddings", 120), ("King Bed Frame", 20),
    ("King Headboard", 130), ("King Mattress", 50),
    ("King Beddings", 150), ("Double Bed Frame", 20),
    ("Double Headboard", 80), ("Double Mattress", 50),
    ("Double Bedding", 120), ("Night Stand", 60),
    ("Single Bed Frame", 20), ("Single Headboard", 75),
    ("Single Mattress", 50), ("Single Beddings", 80),
    ("Desk", 100), ("Chair", 50), ("Patio Set", 150),
]

TOOL = {
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
                "description": "Primary classification of this call.",
            },
            "confidence": {"type": "number", "description": "0.0-1.0 confidence in call_type."},
            "summary": {"type": "string", "description": "1-2 sentence plain-English summary of what happened on the call."},
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
                    "property_type": {"type": "string", "description": "house | condo | townhouse | other | unknown"},
                    "rooms_discussed": {"type": "array", "items": {"type": "string"}},
                    "occupancy": {"type": "string", "description": "occupied | vacant | unknown"},
                },
            },
            "key_points": {"type": "array", "items": {"type": "string"}},
            "action_items": {"type": "array", "items": {"type": "string"}, "description": "What Astra needs to DO next because of this call."},
            "suggested_quote_lines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_name": {"type": "string", "description": "Must match an entry from the provided catalog exactly."},
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
                    "severity": {"type": "string", "description": "low | normal | high | urgent"},
                    "description": {"type": "string"},
                    "callback_number": {"type": "string"},
                },
            },
            "zoho_match_hint": {
                "type": "string",
                "description": "Free-text clue to help match to an existing Staging_Report row — e.g. 'likely matches 830-5 Everson Dr staging' or 'no existing match, new inquiry'.",
            },
        },
        "required": ["call_type", "confidence", "summary"],
    },
}

SYSTEM_PROMPT = f"""You analyze phone-call transcripts from Astra Staging, a Toronto home-staging company. Calls hit line +1-xxx. Agents always identify as "calling from Astra Staging" (agents include Clara, Claire, Ashika). Inbound calls are often customer service issues, sales follow-ups, or cold sales pitches from other companies.

Speaker labels: transcripts are diarized by physical channel. Typically Ch0 = Astra Agent, Ch1 = Customer/Caller. Trust the channel labels.

Your job: populate the record_call_analysis tool. Be conservative:
- If the call is a voicemail bounce, hang-up, or "we're having trouble with your call" system message, classify as `voicemail_or_failed` with empty fields.
- If the caller is selling TO Astra (cold call), classify as `cold_call_inbound` and don't draft action items.
- If the customer reports damage, scheduling issue, or complaint, fill cs_task with severity + callback.
- Only suggest quote lines if rooms/furniture were explicitly discussed. Match names exactly against this catalog:
{json.dumps([n for n, _ in CATALOG])}
- zoho_match_hint should mention any property address / customer name the agent referenced that likely matches an existing staging.

Do NOT invent prices, dates, or customer names not in the transcript."""


def analyze(transcript: str) -> dict:
    headers = {
        "x-api-key": KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-sonnet-4-5",  # Sonnet 4.5 is the latest Sonnet available via public API as of today
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "tools": [TOOL],
        "tool_choice": {"type": "tool", "name": "record_call_analysis"},
        "messages": [
            {"role": "user", "content": f"Transcript:\n\n{transcript}"},
        ],
    }
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload,
        )
    if r.status_code != 200:
        return {"_error": f"{r.status_code}: {r.text[:400]}"}
    body = r.json()
    for block in body.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "record_call_analysis":
            return {"_ok": True, "input": block["input"], "usage": body.get("usage")}
    return {"_error": f"no tool_use block in response: {body}"}


def main() -> int:
    dg_files = sorted(OUT.glob("*.dg.txt"))
    if not dg_files:
        print("No *.dg.txt files found. Run transcribe_deepgram.py first.")
        return 1

    total_in = total_out = 0
    for i, dg in enumerate(dg_files, start=1):
        callid = dg.stem.replace(".dg", "")
        transcript = dg.read_text()
        t0 = time.time()
        result = analyze(transcript)
        elapsed = time.time() - t0

        if "_error" in result:
            print(f"[{i}/{len(dg_files)}] {callid}  ERROR: {result['_error']}")
            continue

        data = result["input"]
        usage = result.get("usage") or {}
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)

        out_path = OUT / f"{callid}.extract.json"
        out_path.write_text(json.dumps(data, indent=2))

        cs = data.get("cs_task")
        quote_n = len(data.get("suggested_quote_lines") or [])
        print(f"[{i}/{len(dg_files)}] {callid}")
        print(f"  type={data['call_type']}  conf={data.get('confidence', '?'):.2f}  "
              f"quote_lines={quote_n}  cs_task={'yes' if cs else 'no'}  ({elapsed:.1f}s)")
        print(f"  summary: {data.get('summary', '')[:160]}")
        if cs:
            print(f"  CS[{cs.get('severity')}]: {cs.get('title')}  (call {cs.get('callback_number', '?')})")
        if data.get("zoho_match_hint"):
            print(f"  zoho: {data['zoho_match_hint'][:150]}")
        print()

    # Sonnet 4.5 pricing: $3/M input, $15/M output
    cost = total_in / 1_000_000 * 3.0 + total_out / 1_000_000 * 15.0
    print(f"Tokens: {total_in} in, {total_out} out → ${cost:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
