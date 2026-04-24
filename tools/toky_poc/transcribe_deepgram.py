"""
Deepgram Nova-3 pass over the same mp3s already downloaded by
fetch_and_transcribe.py. Writes speaker-diarized transcripts into out/*.dg.txt
plus a side-by-side summary vs the Whisper outputs.

Usage:
    .venv/bin/python tools/toky_poc/transcribe_deepgram.py
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
DG_KEY = os.getenv("DEEPGRAM_API_KEY", "").strip()
if not DG_KEY:
    print("ERROR: DEEPGRAM_API_KEY not set in .env", file=sys.stderr)
    sys.exit(2)

DG_URL = "https://api.deepgram.com/v1/listen"
PARAMS = {
    "model": "nova-3",
    "language": "en",
    "punctuate": "true",
    "smart_format": "true",
    "diarize": "true",
    "utterances": "true",
    "multichannel": "true",  # uses separate channels if stereo; no harm on mono
}


def transcribe_mp3(mp3_path: Path) -> dict:
    """Return the parsed Deepgram JSON for this file."""
    headers = {
        "Authorization": f"Token {DG_KEY}",
        "Content-Type": "audio/mpeg",
    }
    with open(mp3_path, "rb") as fh:
        body = fh.read()
    with httpx.Client(timeout=120.0) as client:
        r = client.post(DG_URL, headers=headers, params=PARAMS, content=body)
    if r.status_code != 200:
        return {"_error": f"{r.status_code}: {r.text[:300]}"}
    return r.json()


def format_utterances(result: dict) -> tuple[str, dict]:
    """Render the diarized transcript as Speaker N: lines and return
    alongside useful metadata (duration, cost, speaker count)."""
    if "_error" in result:
        return f"[deepgram error] {result['_error']}", {}

    metadata = result.get("metadata", {})
    duration = metadata.get("duration", 0)
    channels = metadata.get("channels", 1)

    # Prefer top-level utterances (Deepgram groups consecutive same-speaker words)
    utts = result.get("results", {}).get("utterances", []) or []
    speakers_seen: set[int] = set()
    lines: list[str] = []
    if utts:
        for u in utts:
            spk = u.get("speaker")
            if spk is not None:
                speakers_seen.add(spk)
            lbl = f"Speaker {spk}" if spk is not None else "?"
            ch = u.get("channel")
            if ch is not None and channels > 1:
                lbl = f"Ch{ch} Speaker {spk}"
            lines.append(f"{lbl}: {u.get('transcript', '').strip()}")
    else:
        # Fallback: stitch together per-channel transcripts
        for ci, ch in enumerate(result.get("results", {}).get("channels", [])):
            alt = (ch.get("alternatives") or [{}])[0]
            lines.append(f"Ch{ci}: {alt.get('transcript', '').strip()}")

    meta = {
        "duration_s": duration,
        "channels": channels,
        "speakers_seen": sorted(speakers_seen),
        "utterance_count": len(utts),
    }
    return "\n".join(lines), meta


def main() -> int:
    mp3s = sorted(OUT.glob("*.mp3"))
    if not mp3s:
        print(f"No mp3 files found in {OUT}. Run fetch_and_transcribe.py first.")
        return 1

    side_by_side: list[dict] = []
    total_seconds = 0.0
    print(f"Found {len(mp3s)} mp3s. Sending each to Deepgram nova-3...\n")

    for i, mp3 in enumerate(mp3s, start=1):
        callid = mp3.stem
        whisper_txt_path = OUT / f"{callid}.txt"
        whisper = whisper_txt_path.read_text() if whisper_txt_path.exists() else ""

        t0 = time.time()
        result = transcribe_mp3(mp3)
        elapsed = time.time() - t0

        transcript, meta = format_utterances(result)
        dg_path = OUT / f"{callid}.dg.txt"
        dg_path.write_text(transcript)
        (OUT / f"{callid}.dg.json").write_text(json.dumps(result, indent=2))

        total_seconds += meta.get("duration_s") or 0

        print(f"[{i}/{len(mp3s)}] {callid}")
        print(f"  dur={meta.get('duration_s', '?'):.1f}s  "
              f"channels={meta.get('channels', '?')}  "
              f"speakers={meta.get('speakers_seen', [])}  "
              f"utterances={meta.get('utterance_count', 0)}  "
              f"({elapsed:.1f}s)")

        # Print first ~8 utterances so we can eyeball
        preview_lines = transcript.split("\n")[:8]
        for ln in preview_lines:
            print(f"    {ln[:110]}{'…' if len(ln) > 110 else ''}")
        if len(transcript.split("\n")) > 8:
            print(f"    … +{len(transcript.split(chr(10))) - 8} more turns")
        print()

        side_by_side.append({
            "callid": callid,
            "duration_s": meta.get("duration_s"),
            "channels": meta.get("channels"),
            "speakers": meta.get("speakers_seen"),
            "whisper_chars": len(whisper),
            "deepgram_chars": len(transcript),
            "whisper_preview": whisper[:200],
            "deepgram_preview": transcript[:400],
        })

    (OUT / "deepgram_summary.json").write_text(json.dumps(side_by_side, indent=2))

    # Cost estimate: Nova-3 batch $0.0043 + diarization $0.001 = $0.0053/min
    cost_usd = (total_seconds / 60.0) * 0.0053
    print(f"\nTotal audio: {total_seconds/60:.1f} min")
    print(f"Deepgram cost (Nova-3 + diarize): ${cost_usd:.3f}")
    print(f"Full results: {OUT / 'deepgram_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
