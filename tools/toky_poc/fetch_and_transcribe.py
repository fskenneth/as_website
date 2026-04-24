"""
Toky POC: fetch the latest N call recordings and transcribe them with Whisper.

Usage:
    TOKY_API_KEY=... python3 tools/toky_poc/fetch_and_transcribe.py [N]

Defaults to N=10. Writes mp3s + transcripts to tools/toky_poc/out/.

Requires OPENAI_API_KEY in as_website/.env (same key already used by the
consultation dictation feature).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]  # as_website/
load_dotenv(ROOT / ".env")

OUT_DIR = Path(__file__).resolve().parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKY_API_BASE = "https://api.toky.co/v1"
OPENAI_API_BASE = "https://api.openai.com/v1"

TOKY_KEY = os.getenv("TOKY_API_KEY", "").strip()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def _require_keys() -> None:
    missing = []
    if not TOKY_KEY:
        missing.append("TOKY_API_KEY")
    if not OPENAI_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        print(f"ERROR: missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)


def list_recent_calls(limit: int) -> list[dict]:
    """Pull the most recent CDRs. Try /cdrs?limit=... first; fall back to
    /cdrs/by-date across the last 30 days if that endpoint shape is off.
    Prints the raw response shape on first call so we can adjust if needed."""
    headers = {"X-Toky-Key": TOKY_KEY, "Accept": "application/json"}
    with httpx.Client(timeout=30.0) as client:
        # Try simple paginated /cdrs
        try:
            r = client.get(f"{TOKY_API_BASE}/cdrs", headers=headers,
                           params={"limit": limit})
            print(f"[toky] GET /cdrs -> {r.status_code}")
            if r.status_code == 200:
                body = r.json()
                print(f"[toky] top-level keys: {list(body.keys()) if isinstance(body, dict) else 'list'}")
                calls = _extract_calls(body)
                if calls:
                    return calls[:limit]
        except httpx.HTTPError as e:
            print(f"[toky] /cdrs failed: {e}")

        # Fallback: by-date for the last 30 days
        from datetime import date, timedelta
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=30)).isoformat()
        r = client.get(f"{TOKY_API_BASE}/cdrs/by-date", headers=headers,
                       params={"start_date": start, "end_date": end, "limit": limit})
        print(f"[toky] GET /cdrs/by-date {start}..{end} -> {r.status_code}")
        if r.status_code != 200:
            print(r.text[:500])
            r.raise_for_status()
        body = r.json()
        print(f"[toky] top-level keys: {list(body.keys()) if isinstance(body, dict) else 'list'}")
        return _extract_calls(body)[:limit]


def _extract_calls(body) -> list[dict]:
    """Toky wraps list in different envelopes across endpoints. Normalize."""
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("cdrs", "results", "data", "items"):
            if isinstance(body.get(key), list):
                return body[key]
    return []


def get_recording_url(callid: str, cdr: dict) -> str | None:
    """Webhook payloads include record_url directly; list endpoints may not.
    Try the CDR dict first, then fall back to GET /recordings/{callid}."""
    for key in ("record_url", "recording_url", "recording"):
        v = cdr.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    headers = {"X-Toky-Key": TOKY_KEY, "Accept": "application/json"}
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{TOKY_API_BASE}/recordings/{callid}", headers=headers)
        if r.status_code != 200:
            print(f"[toky] recordings/{callid} -> {r.status_code} {r.text[:200]}")
            return None
        body = r.json()
        for key in ("url", "record_url", "recording_url"):
            v = body.get(key) if isinstance(body, dict) else None
            if isinstance(v, str) and v.startswith("http"):
                return v
    return None


def download(url: str, dest: Path) -> bool:
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        r = client.get(url)
        if r.status_code != 200:
            print(f"[download] {dest.name} -> {r.status_code}")
            return False
        dest.write_bytes(r.content)
        return True


def transcribe(mp3: Path) -> str:
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {"model": "whisper-1", "response_format": "text", "language": "en"}
    with open(mp3, "rb") as fh:
        files = {"file": (mp3.name, fh, "audio/mpeg")}
        with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
            r = client.post(f"{OPENAI_API_BASE}/audio/transcriptions",
                            headers=headers, data=data, files=files)
    if r.status_code != 200:
        return f"[whisper error {r.status_code}] {r.text[:300]}"
    return r.text.strip()


def main() -> int:
    _require_keys()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print(f"Fetching {n} most recent Toky calls…")
    calls = list_recent_calls(n)
    print(f"Got {len(calls)} calls")
    if not calls:
        print("No calls returned. Dumping first CDR shape for debug:")
        return 1

    # Save raw CDR list for debugging
    (OUT_DIR / "cdrs.json").write_text(json.dumps(calls, indent=2))
    print(f"Saved raw CDRs → {OUT_DIR / 'cdrs.json'}")

    summary: list[dict] = []
    for i, cdr in enumerate(calls, start=1):
        callid = (cdr.get("callid") or cdr.get("id") or cdr.get("uuid") or f"unknown-{i}")
        direction = cdr.get("direction", "?")
        dur = cdr.get("duration", "?")
        date = cdr.get("date") or cdr.get("created_at") or "?"
        print(f"\n[{i}/{len(calls)}] callid={callid} dir={direction} dur={dur} date={date}")

        url = get_recording_url(callid, cdr)
        if not url:
            print("  no recording URL, skipping")
            summary.append({"callid": callid, "status": "no_url", "transcript": ""})
            continue

        mp3 = OUT_DIR / f"{callid}.mp3"
        if not mp3.exists():
            if not download(url, mp3):
                summary.append({"callid": callid, "status": "download_failed", "transcript": ""})
                continue
        print(f"  mp3 saved → {mp3.name} ({mp3.stat().st_size // 1024} KB)")

        t0 = time.time()
        txt = transcribe(mp3)
        elapsed = time.time() - t0
        print(f"  whisper: {len(txt)} chars in {elapsed:.1f}s")
        print(f"  preview: {txt[:140]}{'…' if len(txt) > 140 else ''}")
        (OUT_DIR / f"{callid}.txt").write_text(txt)
        summary.append({
            "callid": callid, "direction": direction, "duration_s": dur,
            "date": date, "mp3": str(mp3), "transcript_chars": len(txt),
            "preview": txt[:400],
        })

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nAll done. Summary: {OUT_DIR / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
