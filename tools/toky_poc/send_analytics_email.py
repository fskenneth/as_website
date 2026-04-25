"""
Email the three Opus analytics reports to a recipient.

Reads:
  out/analytics_report.md            (all calls)
  out/wins_only_analytics.md         (won deals)
  out/email_analytics_report.md      (emails)

Sends one consolidated HTML email via tools.gmail_sender.GmailSender
(authentic sales@ mailbox; same path the per-call notify uses).

Usage:
    .venv/bin/python tools/toky_poc/send_analytics_email.py [recipient]

Default recipient: fskenneth@gmail.com
"""
from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

ROOT = Path("/var/www/as_website") if Path("/var/www/as_website/tools").exists() else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.gmail_sender import GmailSender

OUT = ROOT / "tools" / "toky_poc" / "out"
RECIPIENT = sys.argv[1] if len(sys.argv) > 1 else "fskenneth@gmail.com"

REPORTS = [
    ("All Toky Calls", OUT / "analytics_report.md"),
    ("Won Deals (Toky)", OUT / "wins_only_analytics.md"),
    ("Customer Emails", OUT / "email_analytics_report.md"),
]


def md_to_html(md: str) -> str:
    """Same minimal converter the /analytics page uses, condensed."""
    lines = md.split("\n")
    out: list[str] = []
    in_ul = in_ol = in_table = False
    table_is_header = True

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            out.append("</ul>"); in_ul = False

    def flush_ol():
        nonlocal in_ol
        if in_ol:
            out.append("</ol>"); in_ol = False

    def flush_table():
        nonlocal in_table, table_is_header
        if in_table:
            out.append("</tbody></table>"); in_table = False; table_is_header = True

    def inline(s: str) -> str:
        s = _html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    for raw in lines:
        stripped = raw.rstrip()
        if not stripped.strip():
            flush_ul(); flush_ol(); flush_table()
            continue

        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                if in_table and table_is_header:
                    out.append("</thead><tbody>")
                    table_is_header = False
                continue
            if not in_table:
                out.append('<table style="border-collapse:collapse;width:100%;font-size:13px;margin:8px 0;"><thead>')
                in_table = True; table_is_header = True
            tag = "th" if table_is_header else "td"
            cell_style = "border:1px solid #ddd;padding:5px 8px;text-align:left;" + ("background:#f6f8fa;font-weight:600;" if tag == "th" else "")
            row_html = "<tr>" + "".join(f'<{tag} style="{cell_style}">{inline(c)}</{tag}>' for c in cells) + "</tr>"
            out.append(row_html)
            continue
        else:
            flush_table()

        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            flush_ul(); flush_ol()
            level = len(m.group(1))
            sizes = {1: "20px", 2: "16px", 3: "14px", 4: "13px", 5: "13px", 6: "13px"}
            margin = "16px 0 6px" if level <= 2 else "10px 0 4px"
            out.append(f'<h{level} style="font-size:{sizes[level]};margin:{margin};">{inline(m.group(2))}</h{level}>')
            continue

        m = re.match(r"^[-*]\s+(.+)$", stripped)
        if m:
            flush_ol()
            if not in_ul:
                out.append('<ul style="margin:4px 0;padding-left:22px;line-height:1.55;">'); in_ul = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        m = re.match(r"^\d+\.\s+(.+)$", stripped)
        if m:
            flush_ul()
            if not in_ol:
                out.append('<ol style="margin:4px 0;padding-left:22px;line-height:1.55;">'); in_ol = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        m = re.match(r"^>\s*(.+)$", stripped)
        if m:
            flush_ul(); flush_ol()
            out.append(f'<blockquote style="border-left:3px solid #3b82f6;margin:6px 0;padding:4px 10px;color:#374151;background:#f9fafb;font-style:italic;">{inline(m.group(1))}</blockquote>')
            continue

        flush_ul(); flush_ol()
        out.append(f'<p style="margin:6px 0;line-height:1.55;">{inline(stripped)}</p>')

    flush_ul(); flush_ol(); flush_table()
    return "\n".join(out)


def main() -> int:
    sections_html: list[str] = []
    sections_text: list[str] = []
    missing: list[str] = []

    for label, path in REPORTS:
        if not path.exists():
            missing.append(f"{label}: {path}")
            continue
        md = path.read_text()
        sections_html.append(
            f'<div style="margin:24px 0;padding:18px 22px;border:1px solid #e4e7eb;border-radius:8px;background:#fff;">'
            f'<h1 style="margin:0 0 8px;font-size:22px;color:#0f172a;border-bottom:2px solid #3b82f6;padding-bottom:6px;">{_html.escape(label)}</h1>'
            f'{md_to_html(md)}'
            f'</div>'
        )
        sections_text.append(f"========== {label} ==========\n\n{md}\n")

    if missing:
        print("WARNING — missing reports, will send what we have:")
        for m in missing:
            print("  -", m)
    if not sections_html:
        print("ERROR: no reports found, aborting send", file=sys.stderr)
        return 2

    portal_link = "https://portal.astrastaging.com/analytics"
    html_body = (
        '<!doctype html><html><body style="margin:0;padding:18px;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;color:#0f172a;">'
        '<div style="max-width:780px;margin:0 auto;">'
        '<h1 style="font-size:24px;margin:0 0 4px;">Astra Staging — Opus analytics</h1>'
        f'<p style="margin:0 0 8px;color:#64748b;font-size:13px;">Three reports below: full Toky corpus, won-deals subset, and the customer-email corpus.</p>'
        f'<p style="margin:0 0 16px;font-size:13px;"><a href="{portal_link}" style="color:#3b82f6;">Open the analytics page in the portal →</a></p>'
        + "".join(sections_html) +
        '</div></body></html>'
    )
    text_body = "\n\n".join(sections_text)

    sender = GmailSender()
    res = sender.send_email(
        to_email=RECIPIENT,
        subject=f"[Astra] Opus analytics — Toky calls + emails ({len(sections_html)} reports)",
        html_content=html_body,
        text_content=text_body,
    )
    if res.get("success"):
        print(f"sent to {RECIPIENT} (message_id={res.get('message_id')})")
        return 0
    print(f"FAILED to send to {RECIPIENT}: {res.get('error')}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
