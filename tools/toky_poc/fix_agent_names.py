"""
One-shot: correct Deepgram/Sonnet misspellings of Astra agent names.
  Ashika  -> Aashika
  Claire  -> Clara

Scope:
  * tools/toky_poc/out/*.dg.txt               (speaker-labeled transcripts)
  * tools/toky_poc/out/*.extract.json         (Sonnet structured output)
  * tools/toky_poc/out/analytics_report.md    (Opus report)
  * zoho_sync.db tables: toky_transcripts.transcript_text,
    toky_extracts.extract_json + summary,
    toky_staging_drafts customer_name / next_step / zoho_match_hint,
    toky_cs_tasks title / description

Idempotent — running twice leaves the data unchanged.
Only touches whole-word occurrences so "Ashika's" also becomes "Aashika's".
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path("/Users/kennethjin/Desktop/development/as_website")
OUT = ROOT / "tools" / "toky_poc" / "out"
DB = ROOT / "data" / "zoho_sync.db"

# Word-boundary regex so "Mashika" or "Clairely" aren't touched. Two patterns
# per replacement to preserve case in each canonical spelling.
REPLACEMENTS = [
    (re.compile(r"\bAshika\b"), "Aashika"),
    (re.compile(r"\bashika\b"), "aashika"),
    (re.compile(r"\bASHIKA\b"), "AASHIKA"),
    (re.compile(r"\bClaire\b"), "Clara"),
    (re.compile(r"\bclaire\b"), "clara"),
    (re.compile(r"\bCLAIRE\b"), "CLARA"),
]


def fix_text(s: str) -> tuple[str, int]:
    if not s:
        return s, 0
    out = s
    total = 0
    for pat, repl in REPLACEMENTS:
        out, n = pat.subn(repl, out)
        total += n
    return out, total


def fix_files() -> None:
    print("\n--- files ---")
    total_hits = 0
    for pattern in ("*.dg.txt", "*.extract.json", "analytics_report.md"):
        for p in sorted(OUT.glob(pattern)):
            txt = p.read_text()
            new, n = fix_text(txt)
            if n:
                p.write_text(new)
                total_hits += n
                print(f"  {p.name}: {n} fix{'es' if n != 1 else ''}")
    print(f"  file total fixes: {total_hits}")


def fix_db() -> None:
    print("\n--- db ---")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        # toky_transcripts
        rows = conn.execute("SELECT callid, transcript_text FROM toky_transcripts").fetchall()
        hits = 0
        for r in rows:
            new, n = fix_text(r["transcript_text"] or "")
            if n:
                conn.execute(
                    "UPDATE toky_transcripts SET transcript_text = ? WHERE callid = ?",
                    (new, r["callid"]),
                )
                hits += n
        print(f"  toky_transcripts: {hits} fixes across {len(rows)} rows")

        # toky_extracts — both the JSON blob AND the denormalized summary column
        rows = conn.execute("SELECT callid, extract_json, summary FROM toky_extracts").fetchall()
        hits_json = hits_sum = 0
        for r in rows:
            new_json, n1 = fix_text(r["extract_json"] or "")
            new_sum, n2 = fix_text(r["summary"] or "")
            if n1 or n2:
                conn.execute(
                    "UPDATE toky_extracts SET extract_json = ?, summary = ? WHERE callid = ?",
                    (new_json, new_sum, r["callid"]),
                )
            hits_json += n1
            hits_sum += n2
        print(f"  toky_extracts:    {hits_json} (json) + {hits_sum} (summary)")

        # toky_staging_drafts
        rows = conn.execute(
            "SELECT id, customer_name, next_step, zoho_match_hint, property_address FROM toky_staging_drafts"
        ).fetchall()
        hits = 0
        for r in rows:
            new_cn, n1 = fix_text(r["customer_name"] or "")
            new_ns, n2 = fix_text(r["next_step"] or "")
            new_zh, n3 = fix_text(r["zoho_match_hint"] or "")
            new_pa, n4 = fix_text(r["property_address"] or "")
            n = n1 + n2 + n3 + n4
            if n:
                conn.execute("""
                    UPDATE toky_staging_drafts
                    SET customer_name=?, next_step=?, zoho_match_hint=?, property_address=?
                    WHERE id=?
                """, (new_cn, new_ns, new_zh, new_pa, r["id"]))
                hits += n
        print(f"  toky_staging_drafts: {hits} fixes")

        # toky_cs_tasks
        rows = conn.execute("SELECT id, title, description FROM toky_cs_tasks").fetchall()
        hits = 0
        for r in rows:
            new_t, n1 = fix_text(r["title"] or "")
            new_d, n2 = fix_text(r["description"] or "")
            if n1 or n2:
                conn.execute(
                    "UPDATE toky_cs_tasks SET title=?, description=? WHERE id=?",
                    (new_t, new_d, r["id"]),
                )
                hits += n1 + n2
        print(f"  toky_cs_tasks: {hits} fixes")

        conn.commit()
    finally:
        conn.close()


def main() -> int:
    fix_files()
    fix_db()
    print("\nDone. Running a quick audit for any remaining occurrences…")

    # Audit: count any remaining misspellings (should be 0 post-fix)
    import subprocess
    for needle in ("Ashika", "Claire"):
        # word-boundary grep — ripgrep not guaranteed, use plain grep with -w
        try:
            out = subprocess.check_output(
                ["grep", "-rwc", needle, str(OUT)],
                text=True, stderr=subprocess.DEVNULL,
            )
            total = sum(int(line.split(":")[-1]) for line in out.splitlines() if line.split(":")[-1].isdigit())
            print(f"  remaining {needle!r} in files: {total}")
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
