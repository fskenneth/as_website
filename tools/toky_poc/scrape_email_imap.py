"""
Scrape every message from kenneth@astrastaging.com (or any IMAP account)
into a local SQLite DB for cross-referencing with Toky calls + Zoho.

Works with any IMAP provider:
  - Google Workspace:   imap.gmail.com (app password required; 2FA must be on)
  - Zoho Mail:          imap.zoho.com
  - Microsoft 365:      outlook.office365.com
  - Most shared hosts:  mail.<domain>

Usage:
  EMAIL_IMAP_HOST=imap.zoho.com  EMAIL_USER=kenneth@astrastaging.com \\
  EMAIL_PASSWORD='<app password>' \\
  .venv/bin/python tools/toky_poc/scrape_email_imap.py [--limit 50000]

Writes to data/email.db — a single table with one row per message:
  id, message_id, thread_id, date, from_addr, to_addrs, cc, subject,
  body_text, body_html, has_attachment, labels_or_folder

Parallel: pulls metadata + bodies in batches, writes in the main thread
to avoid SQLite contention.
"""
from __future__ import annotations

import argparse
import email
import email.policy
import imaplib
import os
import re
import sqlite3
import sys
import time
from email.header import decode_header
from pathlib import Path
from typing import Optional

ROOT = Path("/Users/kennethjin/Desktop/development/as_website")
EMAIL_DB = ROOT / "data" / "email.db"


def _decode(raw: Optional[str]) -> str:
    if not raw:
        return ""
    try:
        parts = decode_header(raw)
    except Exception:
        return str(raw)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                out.append(text.decode(charset or "utf-8", errors="replace"))
            except LookupError:
                out.append(text.decode("utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            folder TEXT,
            date_utc TEXT,
            from_addr TEXT,
            to_addrs TEXT,
            cc_addrs TEXT,
            subject TEXT,
            body_text TEXT,
            body_html TEXT,
            has_attachment INTEGER DEFAULT 0,
            raw_size INTEGER,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_from ON emails(from_addr)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date_utc)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_subject ON emails(subject)")
    conn.commit()


def _extract_bodies(msg: email.message.Message) -> tuple[str, str, bool]:
    text_body, html_body = "", ""
    has_attachment = False
    for part in msg.walk():
        cd = part.get("Content-Disposition") or ""
        ct = part.get_content_type()
        if "attachment" in cd.lower() or part.get_filename():
            has_attachment = True
            continue
        if ct == "text/plain" and not text_body:
            try:
                text_body = part.get_content()
            except Exception:
                text_body = part.get_payload(decode=True) or b""
                text_body = text_body.decode(errors="replace") if isinstance(text_body, bytes) else str(text_body)
        elif ct == "text/html" and not html_body:
            try:
                html_body = part.get_content()
            except Exception:
                html_body = part.get_payload(decode=True) or b""
                html_body = html_body.decode(errors="replace") if isinstance(html_body, bytes) else str(html_body)
    return text_body, html_body, has_attachment


def scrape(host: str, user: str, password: str, folder: str = "INBOX",
           use_ssl: bool = True, limit: int = 0) -> dict:
    _conn = sqlite3.connect(EMAIL_DB)
    _ensure_schema(_conn)
    seen = {r[0] for r in _conn.execute("SELECT message_id FROM emails WHERE folder = ?", (folder,)).fetchall()}

    print(f"connecting to {host}...")
    M = imaplib.IMAP4_SSL(host) if use_ssl else imaplib.IMAP4(host)
    M.login(user, password)

    if folder == "__ALL__":
        # Pull all folders
        ok, folders = M.list()
        folder_list = []
        for f in folders:
            # Typical response: b'(\\HasNoChildren) "/" "INBOX"'
            m = re.search(rb'"([^"]+)"$', f)
            if m:
                folder_list.append(m.group(1).decode())
        print(f"found {len(folder_list)} folders")
    else:
        folder_list = [folder]

    ins = 0
    skipped = 0
    for f in folder_list:
        try:
            ok, _resp = M.select(f"\"{f}\"", readonly=True)
        except imaplib.IMAP4.error as e:
            print(f"  skip {f}: {e}")
            continue
        if ok != "OK":
            print(f"  skip {f}: select returned {ok}")
            continue
        try:
            ok, data = M.search(None, "ALL")
        except imaplib.IMAP4.error as e:
            print(f"  skip {f}: search err {e}")
            continue
        if ok != "OK":
            continue
        ids = data[0].split()
        print(f"  {f}: {len(ids)} messages")
        target_ids = ids if limit <= 0 else ids[-limit:]
        for i, n in enumerate(target_ids, 1):
            try:
                ok, msg_data = M.fetch(n, "(RFC822)")
                if ok != "OK" or not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                mid = _decode(msg.get("Message-ID", "")) or f"{f}:{n.decode()}"
                if mid in seen:
                    skipped += 1; continue
                seen.add(mid)
                text_body, html_body, has_att = _extract_bodies(msg)
                _conn.execute("""
                    INSERT OR IGNORE INTO emails
                        (message_id, folder, date_utc, from_addr, to_addrs, cc_addrs,
                         subject, body_text, body_html, has_attachment, raw_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mid, f, _decode(msg.get("Date","")),
                    _decode(msg.get("From","")),
                    _decode(msg.get("To","")),
                    _decode(msg.get("Cc","")),
                    _decode(msg.get("Subject","")),
                    text_body[:200_000], html_body[:200_000],
                    1 if has_att else 0,
                    len(raw),
                ))
                ins += 1
                if ins % 500 == 0:
                    _conn.commit()
                    print(f"    ...{ins} inserted")
            except Exception as e:
                print(f"    err on {n}: {e}")
    _conn.commit()
    _conn.close()
    M.logout()
    return {"inserted": ins, "skipped": skipped}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("EMAIL_IMAP_HOST"))
    ap.add_argument("--user", default=os.environ.get("EMAIL_USER"))
    ap.add_argument("--password", default=os.environ.get("EMAIL_PASSWORD"))
    ap.add_argument("--folder", default=os.environ.get("EMAIL_FOLDER", "INBOX"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-ssl", action="store_true")
    args = ap.parse_args()
    if not (args.host and args.user and args.password):
        print("Missing credentials. Set EMAIL_IMAP_HOST, EMAIL_USER, EMAIL_PASSWORD", file=sys.stderr)
        sys.exit(2)
    t0 = time.time()
    r = scrape(args.host, args.user, args.password, args.folder, not args.no_ssl, args.limit)
    print(f"done in {time.time()-t0:.0f}s — inserted {r['inserted']} new, skipped {r['skipped']} dupes")
    print(f"DB: {EMAIL_DB}")
