"""
Process only the Toky calls that belong to won Zoho stagings
(as identified by wins_mapping.json). Runs the end-to-end pipeline
directly (no webhook detour), writes to toky_calls/transcripts/extracts
in the same DB the portal reads from.

Parallel via asyncio (concurrency 3 — respects the Anthropic output-token
rate limit we hit in the 500 backfill).
"""
import asyncio
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path("/Users/kennethjin/Desktop/development/as_website")
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from as_webapp.as_portal_api import toky_service

DB_PATH = ROOT / "data" / "zoho_sync.db"
OUT = ROOT / "tools" / "toky_poc" / "out"

mapping = json.loads((OUT / "wins_mapping.json").read_text())
new_calls = mapping["new_calls"]
print(f"calls to process: {len(new_calls)}")

TOKY_KEY = os.environ["TOKY_API_KEY"]
HDR = {"X-Toky-Key": TOKY_KEY, "Accept": "application/json"}


async def fetch_all_cdrs() -> dict:
    url = "https://api.toky.co/v1/cdrs?limit=500"
    out: dict = {}
    async with httpx.AsyncClient(timeout=60.0) as c:
        while url and len(out) < 12000:
            r = await c.get(url, headers=HDR)
            if r.status_code != 200:
                break
            d = r.json()
            for cdr in d.get("results", []):
                if cdr.get("callid"):
                    out[cdr["callid"]] = cdr
            url = d.get("next")
    return out


def process_one_sync(cdr: dict) -> dict:
    """process_call in its own thread with its own sqlite connection."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        toky_service.insert_cdr(conn, cdr)
        # Claim it (so parallel scripts + the live worker don't collide)
        conn.execute(
            "UPDATE toky_calls SET status='processing' WHERE callid=? AND status='pending'",
            (cdr["callid"],),
        )
        conn.commit()
        try:
            return toky_service.process_call(conn, cdr)
        except Exception as e:
            toky_service.mark_done(conn, cdr["callid"], status="error", error=str(e)[:500])
            return {"callid": cdr["callid"], "error": str(e)[:100]}
    finally:
        conn.close()


async def main():
    print("fetching all CDRs...")
    cdrs = await fetch_all_cdrs()
    print(f"got {len(cdrs)} CDRs")

    targets = [cdrs[c] for c in new_calls if c in cdrs]
    print(f"matched callid CDRs: {len(targets)} / {len(new_calls)}")

    sem = asyncio.Semaphore(3)
    done = 0
    errs = 0
    start = time.time()

    async def run(cdr):
        nonlocal done, errs
        async with sem:
            res = await asyncio.to_thread(process_one_sync, cdr)
        done += 1
        if res.get("error"):
            errs += 1
        if done % 10 == 0 or done == len(targets):
            elapsed = time.time() - start
            print(f"  {done}/{len(targets)}  errors={errs}  "
                  f"({done / max(elapsed, 1):.1f}/s)")

    await asyncio.gather(*[run(cdr) for cdr in targets])

    elapsed = time.time() - start
    print(f"\nfinished in {elapsed:.0f}s  done={done}  errors={errs}")


if __name__ == "__main__":
    asyncio.run(main())
