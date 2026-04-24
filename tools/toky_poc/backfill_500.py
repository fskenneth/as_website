"""
Backfill the 500 most-recent Toky calls end-to-end:
    CDR list -> download mp3 -> Deepgram Nova-3 (diarize + multichannel)
             -> Claude Sonnet 4.5 structured extraction -> per-call JSON

Parallel + resumable. Rerun is safe: already-processed callids are skipped.

Skip policy: calls with duration < 4s are marked 'noise' and not sent to
Deepgram or Sonnet (they're 100% "trouble with your call" system messages).

Usage:
    .venv/bin/python tools/toky_poc/backfill_500.py [N]   # default N=500

Output:
    out/<callid>.mp3
    out/<callid>.dg.txt           # speaker-labeled transcript
    out/<callid>.dg.json          # raw deepgram response
    out/<callid>.extract.json     # sonnet structured output
    out/backfill_log.jsonl        # one line per call: status + cost-contrib
    out/backfill_summary.json     # end-of-run aggregate
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
LOG_PATH = OUT / "backfill_log.jsonl"

TOKY_KEY = os.getenv("TOKY_API_KEY", "").strip()
DG_KEY = os.getenv("DEEPGRAM_API_KEY", "").strip()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
for name, v in [("TOKY_API_KEY", TOKY_KEY), ("DEEPGRAM_API_KEY", DG_KEY), ("ANTHROPIC_API_KEY", ANTHROPIC_KEY)]:
    if not v:
        print(f"ERROR: {name} missing from .env", file=sys.stderr); sys.exit(2)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
NOISE_THRESHOLD_S = 4

DG_URL = "https://api.deepgram.com/v1/listen"
DG_PARAMS = {
    "model": "nova-3",
    "language": "en",
    "punctuate": "true",
    "smart_format": "true",
    "diarize": "true",
    "utterances": "true",
    "multichannel": "true",
    # nova-3 uses `keyterm` (not `keywords`); boost proper nouns the model hears
    "keyterm": "Astra",
}

CATALOG_NAMES = [
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

SONNET_TOOL = {
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
                "description": "Signals useful for win/loss analytics.",
                "properties": {
                    "objections_raised": {"type": "array", "items": {"type": "string"}},
                    "closing_phrases_used": {"type": "array", "items": {"type": "string"}},
                    "next_step_committed": {"type": "string"},
                    "outcome": {
                        "type": "string",
                        "description": "won | lost | pending | n/a",
                    },
                },
            },
        },
        "required": ["call_type", "confidence", "summary"],
    },
}

SONNET_SYSTEM = f"""You analyze phone-call transcripts from Astra Staging, a Toronto home-staging company. Toky records stereo; Ch0 = agent, Ch1 = caller. Trust channel labels. Agents include Clara, Claire, Ashika; they self-identify as 'Astra Staging'.

Populate record_call_analysis. Be conservative:
- voicemail/system-message/hang-up → call_type=voicemail_or_failed, empty fields
- someone selling TO Astra → cold_call_inbound, no action items
- damage/complaint → cs_task with severity (low|normal|high|urgent) + callback_number
- sales_signal fields: pull objections ('price is too high', 'need to think'), closing phrases, and classify outcome (won/lost/pending/n/a)
- Only suggest quote lines if furniture was explicitly discussed. Exact names from catalog:
{json.dumps(CATALOG_NAMES)}
- zoho_match_hint: any address or name the agent used that likely maps to a Staging_Report row.

Do NOT invent prices, dates, or names not in transcript."""


@dataclass
class CallResult:
    callid: str
    status: str  # "done" | "noise_skipped" | "no_url" | "download_err" | "dg_err" | "sonnet_err"
    duration_s: Optional[float] = None
    dg_seconds: Optional[float] = None
    sonnet_in: Optional[int] = None
    sonnet_out: Optional[int] = None
    error: Optional[str] = None


async def list_cdrs(n: int) -> list[dict]:
    headers = {"X-Toky-Key": TOKY_KEY, "Accept": "application/json"}
    out = []
    async with httpx.AsyncClient(timeout=60.0) as c:
        url = f"https://api.toky.co/v1/cdrs?limit={min(500, n)}"
        while url and len(out) < n:
            r = await c.get(url, headers=headers)
            r.raise_for_status()
            d = r.json()
            out.extend(d.get("results", []))
            url = d.get("next") if len(out) < n else None
            if url:
                await asyncio.sleep(0.05)
    return out[:n]


async def download_mp3(client: httpx.AsyncClient, cdr: dict, callid: str) -> bool:
    dest = OUT / f"{callid}.mp3"
    if dest.exists() and dest.stat().st_size > 0:
        return True
    # Toky list endpoint doesn't include record_url; fetch recording
    # URL and then download.
    headers = {"X-Toky-Key": TOKY_KEY, "Accept": "application/json"}
    r = await client.get(f"https://api.toky.co/v1/recordings/{callid}", headers=headers)
    if r.status_code != 200:
        return False
    body = r.json()
    url = None
    if isinstance(body, dict):
        for k in ("url", "record_url", "recording_url"):
            v = body.get(k)
            if isinstance(v, str) and v.startswith("http"):
                url = v; break
    if not url:
        return False
    r2 = await client.get(url, follow_redirects=True)
    if r2.status_code != 200:
        return False
    dest.write_bytes(r2.content)
    return True


async def run_deepgram(client: httpx.AsyncClient, callid: str) -> tuple[str, dict]:
    mp3 = OUT / f"{callid}.mp3"
    dg_txt = OUT / f"{callid}.dg.txt"
    dg_json = OUT / f"{callid}.dg.json"
    if dg_txt.exists() and dg_json.exists():
        return dg_txt.read_text(), json.loads(dg_json.read_text())

    headers = {"Authorization": f"Token {DG_KEY}", "Content-Type": "audio/mpeg"}
    body = mp3.read_bytes()
    r = await client.post(DG_URL, headers=headers, params=DG_PARAMS, content=body)
    r.raise_for_status()
    result = r.json()
    dg_json.write_text(json.dumps(result))

    utts = result.get("results", {}).get("utterances", []) or []
    chans = result.get("metadata", {}).get("channels", 1)
    lines = []
    if utts:
        for u in utts:
            spk = u.get("speaker")
            ch = u.get("channel")
            lbl = "Speaker ?"
            if spk is not None:
                lbl = f"Speaker {spk}"
            if ch is not None and chans > 1:
                lbl = f"Ch{ch} Speaker {spk if spk is not None else '?'}"
            lines.append(f"{lbl}: {u.get('transcript','').strip()}")
    else:
        for ci, c in enumerate(result.get("results", {}).get("channels", [])):
            alt = (c.get("alternatives") or [{}])[0]
            lines.append(f"Ch{ci}: {alt.get('transcript','').strip()}")
    txt = "\n".join(lines)
    dg_txt.write_text(txt)
    return txt, result


async def run_sonnet(client: httpx.AsyncClient, callid: str, transcript: str, cdr: dict) -> tuple[dict, dict]:
    out_path = OUT / f"{callid}.extract.json"
    if out_path.exists():
        return json.loads(out_path.read_text()), {"cached": True}
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    context_block = (
        f"Metadata: direction={cdr.get('direction')}  duration={cdr.get('duration')}s  "
        f"agent={cdr.get('agent_id')}  from={cdr.get('from')}  to={cdr.get('received_on_number')}  "
        f"init_dt={cdr.get('init_dt')}"
    )
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 2048,
        "system": [
            # Prompt-cache the (large, static) system prompt + catalog
            {"type": "text", "text": SONNET_SYSTEM, "cache_control": {"type": "ephemeral"}},
        ],
        "tools": [SONNET_TOOL],
        "tool_choice": {"type": "tool", "name": "record_call_analysis"},
        "messages": [
            {"role": "user", "content": f"{context_block}\n\nTranscript:\n\n{transcript}"},
        ],
    }
    # Retry on 429 (anthropic's output-tokens-per-minute limit bites hard
    # when we fire 8 calls in parallel). Honor retry-after when present.
    for attempt in range(8):
        r = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        if r.status_code == 429:
            try:
                wait = float(r.headers.get("retry-after", "10"))
            except ValueError:
                wait = 10.0
            wait = max(wait, 5.0 * (attempt + 1))  # backoff floor
            await asyncio.sleep(wait)
            continue
        break
    if r.status_code != 200:
        raise RuntimeError(f"sonnet {r.status_code}: {r.text[:300]}")
    body = r.json()
    usage = body.get("usage", {})
    for block in body.get("content", []):
        if block.get("type") == "tool_use":
            data = block["input"]
            out_path.write_text(json.dumps(data, indent=2))
            return data, usage
    raise RuntimeError(f"no tool_use in response: {body}")


def log(entry: dict) -> None:
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


async def process_one(
    sem: asyncio.Semaphore, client: httpx.AsyncClient, cdr: dict,
) -> CallResult:
    callid = cdr.get("callid") or cdr.get("id") or ""
    try:
        dur = int(cdr.get("duration") or 0)
    except Exception:
        dur = 0

    # Skip noise outright — save Deepgram + Sonnet round-trips.
    if dur < NOISE_THRESHOLD_S:
        res = CallResult(callid, "noise_skipped", duration_s=dur)
        log({"callid": callid, "status": res.status, "duration_s": dur})
        return res

    async with sem:
        # Idempotent: if extract.json already exists, skip everything.
        if (OUT / f"{callid}.extract.json").exists():
            res = CallResult(callid, "done", duration_s=dur)
            log({"callid": callid, "status": "done_cached"})
            return res

        try:
            ok = await download_mp3(client, cdr, callid)
            if not ok:
                log({"callid": callid, "status": "no_url"})
                return CallResult(callid, "no_url", duration_s=dur)

            t0 = time.time()
            transcript, dg_result = await run_deepgram(client, callid)
            dg_dur = dg_result.get("metadata", {}).get("duration", 0)
            _ = time.time() - t0

            _, usage = await run_sonnet(client, callid, transcript, cdr)

            res = CallResult(
                callid, "done",
                duration_s=dur,
                dg_seconds=dg_dur,
                sonnet_in=usage.get("input_tokens"),
                sonnet_out=usage.get("output_tokens"),
            )
            log({
                "callid": callid, "status": "done", "duration_s": dur,
                "dg_seconds": dg_dur,
                "sonnet_in": usage.get("input_tokens"),
                "sonnet_out": usage.get("output_tokens"),
                "cache_read": usage.get("cache_read_input_tokens"),
                "cache_write": usage.get("cache_creation_input_tokens"),
            })
            return res
        except Exception as e:
            msg = str(e)[:300]
            log({"callid": callid, "status": "error", "error": msg})
            return CallResult(callid, "error", duration_s=dur, error=msg)


async def main() -> int:
    print(f"Fetching {N} most-recent CDRs from Toky...")
    cdrs = await list_cdrs(N)
    print(f"Got {len(cdrs)} CDRs")

    # Drop to 3 in parallel — keeps Sonnet under the 8k output-tokens/min cap.
    sem = asyncio.Semaphore(3)
    timeout = httpx.Timeout(connect=15.0, read=180.0, write=60.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        results: list[CallResult] = []
        done = 0
        for batch_start in range(0, len(cdrs), 40):
            batch = cdrs[batch_start:batch_start + 40]
            batch_results = await asyncio.gather(
                *[process_one(sem, client, cdr) for cdr in batch],
                return_exceptions=False,
            )
            results.extend(batch_results)
            done += len(batch)
            progress_done = sum(1 for r in results if r.status == "done")
            noise = sum(1 for r in results if r.status == "noise_skipped")
            errs = sum(1 for r in results if r.status not in ("done", "noise_skipped"))
            print(f"  ...{done}/{len(cdrs)}  done={progress_done} noise={noise} err={errs}")

    # Summary
    total_dg_sec = sum(r.dg_seconds or 0 for r in results if r.status == "done")
    total_sonnet_in = sum(r.sonnet_in or 0 for r in results if r.status == "done")
    total_sonnet_out = sum(r.sonnet_out or 0 for r in results if r.status == "done")

    # Deepgram: nova-3 + diarize ≈ $0.0053/min
    dg_cost = (total_dg_sec / 60.0) * 0.0053
    # Sonnet 4.5 base: $3/M in, $15/M out (ignoring the 90% cache discount for safety)
    sonnet_cost = total_sonnet_in / 1_000_000 * 3.0 + total_sonnet_out / 1_000_000 * 15.0

    summary = {
        "requested": N,
        "received": len(cdrs),
        "done": sum(1 for r in results if r.status == "done"),
        "noise_skipped": sum(1 for r in results if r.status == "noise_skipped"),
        "errors": sum(1 for r in results if r.status not in ("done", "noise_skipped")),
        "dg_total_seconds": total_dg_sec,
        "dg_cost_usd": round(dg_cost, 3),
        "sonnet_input_tokens": total_sonnet_in,
        "sonnet_output_tokens": total_sonnet_out,
        "sonnet_cost_usd": round(sonnet_cost, 3),
        "total_cost_usd": round(dg_cost + sonnet_cost, 3),
    }
    (OUT / "backfill_summary.json").write_text(json.dumps(summary, indent=2))
    print()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
