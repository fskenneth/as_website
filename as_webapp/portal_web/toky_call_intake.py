"""
Call Intake — portal page showing structured extracts from Toky calls.

Two views:
  /toky_call_intake             : list of calls (filter: all / cs / drafts / noise)
  /toky_call_intake/{callid}    : full detail (transcript + extract + actions)

POST handlers to flip CS task / draft status:
  /toky_call_intake/cs/{id}/resolve
  /toky_call_intake/cs/{id}/reopen
  /toky_call_intake/draft/{id}/approve
  /toky_call_intake/draft/{id}/reject

Auth: session cookie (same SESSION_COOKIE_NAME used by the rest of the portal).
Signed-out users bounce to /signin.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime

from fasthtml.common import (
    A, Body, Button, Div, Form, H1, H2, H3, Head, Html, Input, Label,
    Link, Main, Meta, P, Pre, Script, Span, Style, Table, Tbody, Td, Th,
    Thead, Title, Tr, NotStr, to_xml,
)
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from as_webapp.as_portal_api.employees_db import get_user_by_session

SESSION_COOKIE_NAME = "astra_session"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZOHO_DB = os.path.join(ROOT, "data", "zoho_sync.db")


def _conn():
    c = sqlite3.connect(ZOHO_DB)
    c.row_factory = sqlite3.Row
    return c


def _current_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    return get_user_by_session(token)


# ---------------- styling ----------------

_CSS = """
:root {
  --bg: #f6f7f9; --surface: #ffffff; --text: #111418; --muted: #5b6470;
  --border: #e4e7eb; --accent: #3b82f6; --accent-hover: #2563eb;
  --urgent: #dc2626; --high: #f59e0b; --normal: #6366f1; --low: #94a3b8;
  --sales-new: #10b981; --sales-followup: #3b82f6; --scheduling: #8b5cf6;
  --cs: #dc2626; --noise: #94a3b8; --cold: #a16207;
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  font-size:14px; line-height:1.5; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
header.app { background:var(--surface); border-bottom:1px solid var(--border);
  padding:12px 24px; display:flex; align-items:center; gap:16px; }
header.app h1 { margin:0; font-size:18px; }
main { max-width:1200px; margin:20px auto; padding:0 16px; }
.nav { display:flex; gap:4px; margin-bottom:16px; flex-wrap:wrap; }
.nav a { padding:6px 12px; border-radius:6px; background:var(--surface);
  border:1px solid var(--border); color:var(--text); font-weight:500; }
.nav a.active { background:var(--accent); color:#fff; border-color:var(--accent); }
.nav a:hover { text-decoration:none; background:#e9eef5; }
.nav a.active:hover { background:var(--accent-hover); }
.card { background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:14px 16px; margin-bottom:10px; display:flex; gap:14px; align-items:flex-start; }
.card:hover { border-color:var(--accent); }
.badge { display:inline-block; padding:2px 8px; border-radius:999px;
  font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.03em; }
.badge.sales_new_lead { background:#d1fae5; color:#065f46; }
.badge.sales_follow_up { background:#dbeafe; color:#1e40af; }
.badge.scheduling { background:#ede9fe; color:#5b21b6; }
.badge.customer_service_issue { background:#fee2e2; color:#991b1b; }
.badge.cold_call_inbound { background:#fef3c7; color:#92400e; }
.badge.voicemail_or_failed { background:#e5e7eb; color:#374151; }
.badge.other { background:#e5e7eb; color:#374151; }
.badge.urgent { background:var(--urgent); color:#fff; }
.badge.high { background:var(--high); color:#fff; }
.badge.normal { background:var(--normal); color:#fff; }
.badge.low { background:var(--low); color:#fff; }
.meta { color:var(--muted); font-size:12px; }
.summary { margin:6px 0 0; }
.call-head { flex:1; min-width:0; }
.call-meta-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; font-size:12px; }
.arrow { color:var(--muted); font-size:13px; }
.section { background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:16px; margin-bottom:12px; }
.section h2 { margin:0 0 8px; font-size:14px; text-transform:uppercase;
  letter-spacing:.04em; color:var(--muted); font-weight:600; }
.kv { display:grid; grid-template-columns:160px 1fr; gap:4px 12px; font-size:13px; }
.kv dt { color:var(--muted); }
.kv dd { margin:0; }
.transcript { background:#f9fafb; padding:12px; border-radius:6px; font-size:13px;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace; white-space:pre-wrap; }
.btn { display:inline-block; padding:6px 14px; border-radius:6px; border:1px solid var(--border);
  background:var(--surface); cursor:pointer; font-size:13px; font-weight:500; }
.btn:hover { border-color:var(--accent); }
.btn-primary { background:var(--accent); color:#fff; border-color:var(--accent); }
.btn-primary:hover { background:var(--accent-hover); }
.btn-danger { background:#fee2e2; color:#991b1b; border-color:#fecaca; }
.pill { display:inline-block; padding:2px 8px; background:#f3f4f6; border-radius:999px;
  font-size:12px; color:var(--muted); margin-right:4px; }
.empty { text-align:center; padding:40px; color:var(--muted); }
.toolbar { display:flex; gap:8px; align-items:center; margin-bottom:12px; flex-wrap:wrap; }
"""


def _page(title: str, *body_children) -> HTMLResponse:
    doc = Html(
        Head(
            Title(f"{title} · Astra Staging"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width,initial-scale=1"),
            Style(_CSS),
        ),
        Body(
            Div(
                H1("Call Intake"),
                Span("Toky → Deepgram → Sonnet → drafts", cls="meta"),
                A("← Portal", href="/portal", style="margin-left:auto;"),
                cls="app",
            ),
            Main(*body_children),
        ),
        lang="en",
    )
    rendered = to_xml(doc)
    if not rendered.lstrip().lower().startswith("<!doctype"):
        rendered = "<!doctype html>\n" + rendered
    return HTMLResponse(rendered)


def _filter_clause(view: str) -> tuple[str, list]:
    """Translate the view query param into a SQL WHERE clause."""
    if view == "cs":
        return " AND EXISTS (SELECT 1 FROM toky_cs_tasks t WHERE t.callid = c.callid AND t.status = 'open')", []
    if view == "drafts":
        return " AND EXISTS (SELECT 1 FROM toky_staging_drafts d WHERE d.callid = c.callid AND d.status = 'draft')", []
    if view == "noise":
        return " AND e.call_type IN ('voicemail_or_failed', 'cold_call_inbound', 'other')", []
    if view == "real":
        return " AND (e.call_type IS NOT NULL AND e.call_type NOT IN ('voicemail_or_failed', 'cold_call_inbound'))", []
    return "", []


_VIEWS = [
    ("real", "Real calls"),
    ("cs", "CS open"),
    ("drafts", "Drafts to review"),
    ("all", "All"),
    ("noise", "Noise"),
]


def _fmt_dt(s: str | None) -> str:
    if not s:
        return ""
    try:
        dt = datetime.fromisoformat(s.replace(" ", "T"))
        return dt.strftime("%b %d  %H:%M")
    except Exception:
        return s


def _fmt_dur(sec) -> str:
    try:
        s = int(sec or 0)
    except (ValueError, TypeError):
        return "?"
    return f"{s // 60}:{s % 60:02d}"


def _fetch_list(view: str, limit: int = 200) -> list[dict]:
    clause, params = _filter_clause(view)
    q = f"""
        SELECT c.callid, c.direction, c.agent_id, c.from_number, c.to_number,
               c.duration_s, c.init_dt, c.status AS proc_status,
               e.call_type, e.confidence, e.summary,
               (SELECT COUNT(*) FROM toky_cs_tasks t WHERE t.callid = c.callid AND t.status = 'open') AS open_cs,
               (SELECT COUNT(*) FROM toky_staging_drafts d WHERE d.callid = c.callid AND d.status = 'draft') AS open_draft
        FROM toky_calls c
        LEFT JOIN toky_extracts e ON e.callid = c.callid
        WHERE 1 = 1 {clause}
        ORDER BY c.init_dt DESC, c.received_at DESC
        LIMIT ?
    """
    params.append(limit)
    with _conn() as conn:
        rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def _fetch_counts() -> dict:
    """Header counts for the nav tabs."""
    with _conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM toky_calls").fetchone()[0]
        real = conn.execute("""
            SELECT COUNT(*) FROM toky_calls c
            JOIN toky_extracts e ON e.callid = c.callid
            WHERE e.call_type IS NOT NULL
              AND e.call_type NOT IN ('voicemail_or_failed', 'cold_call_inbound')
        """).fetchone()[0]
        cs = conn.execute("SELECT COUNT(*) FROM toky_cs_tasks WHERE status = 'open'").fetchone()[0]
        drafts = conn.execute("SELECT COUNT(*) FROM toky_staging_drafts WHERE status = 'draft'").fetchone()[0]
        noise = conn.execute("""
            SELECT COUNT(*) FROM toky_calls c
            JOIN toky_extracts e ON e.callid = c.callid
            WHERE e.call_type IN ('voicemail_or_failed', 'cold_call_inbound', 'other')
        """).fetchone()[0]
    return {"all": total, "real": real, "cs": cs, "drafts": drafts, "noise": noise}


def _render_card(row: dict):
    ct = row.get("call_type") or "—"
    direction = row.get("direction") or "?"
    agent = row.get("agent_id") or "?"
    caller = row.get("from_number") if direction == "inbound" else row.get("to_number")
    summary = row.get("summary") or ""

    badges = [Span(ct.replace("_", " "), cls=f"badge {ct}")]
    if row.get("open_cs"):
        badges.append(Span(f"{row['open_cs']} CS open", cls="badge urgent"))
    if row.get("open_draft"):
        badges.append(Span(f"{row['open_draft']} draft", cls="badge normal"))

    return A(
        Div(
            Div(*badges, style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px;"),
            Div(
                Span(_fmt_dt(row.get("init_dt")), cls="meta"),
                Span(" · ", cls="meta"),
                Span(f"{direction}  {_fmt_dur(row.get('duration_s'))}", cls="meta"),
                Span(" · ", cls="meta"),
                Span(f"agent: {agent}", cls="meta"),
                Span(" · ", cls="meta"),
                Span(f"caller: {caller or '?'}", cls="meta"),
                cls="call-meta-row",
            ),
            Div(summary[:260] + ("…" if len(summary) > 260 else ""), cls="summary"),
            cls="call-head",
        ),
        Span("›", cls="arrow", style="font-size:24px;"),
        href=f"/toky_call_intake/{row['callid']}",
        cls="card",
        style="color:inherit;",
    )


def _render_analytics_report() -> str:
    """Minimal markdown → HTML converter for the Opus analytics report.
    Supports: # / ## / ### headings, **bold**, tables, ordered/unordered lists,
    blockquotes, inline code. Anything fancier and we'd add a real lib."""
    import html as _html
    import re

    path = os.path.join(ROOT, "tools", "toky_poc", "out", "analytics_report.md")
    if not os.path.exists(path):
        return "<p>No analytics report has been generated yet. Run <code>tools/toky_poc/analytics_opus.py</code>.</p>"
    md = open(path).read()
    lines = md.split("\n")
    out: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
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
            out.append("</tbody></table></div>"); in_table = False; table_is_header = True

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

        # Tables
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                # separator row
                if in_table and table_is_header:
                    out[-1] = out[-1].replace("<tr>", "<tr>")
                    out.append("</thead><tbody>")
                    table_is_header = False
                continue
            if not in_table:
                out.append('<div class="tablewrap"><table><thead>')
                in_table = True
                table_is_header = True
            tag = "th" if table_is_header else "td"
            row_html = "<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>"
            out.append(row_html)
            continue
        else:
            flush_table()

        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            flush_ul(); flush_ol()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            continue

        # Unordered list
        m = re.match(r"^[-*]\s+(.+)$", stripped)
        if m:
            flush_ol()
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        # Ordered list
        m = re.match(r"^\d+\.\s+(.+)$", stripped)
        if m:
            flush_ul()
            if not in_ol:
                out.append("<ol>"); in_ol = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue

        # Blockquote
        m = re.match(r"^>\s*(.+)$", stripped)
        if m:
            flush_ul(); flush_ol()
            out.append(f"<blockquote>{inline(m.group(1))}</blockquote>")
            continue

        # Paragraph
        flush_ul(); flush_ol()
        out.append(f"<p>{inline(stripped)}</p>")

    flush_ul(); flush_ol(); flush_table()
    return "\n".join(out)


def register(rt):
    @rt("/toky_call_intake")
    def intake_list(request: Request):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)

        view = (request.query_params.get("view") or "real").lower()
        if view not in {v for v, _ in _VIEWS}:
            view = "real"

        rows = _fetch_list(view)
        counts = _fetch_counts()

        nav = Div(
            *[A(
                f"{label} ",
                Span(f"({counts.get(vid, 0)})", cls="meta"),
                href=f"/toky_call_intake?view={vid}",
                cls=("active" if vid == view else ""),
            ) for vid, label in _VIEWS],
            cls="nav",
        )

        if not rows:
            body = Div(
                P("No calls match this filter yet."),
                P("Once the Toky webhook is registered, incoming calls will appear here within ~15 seconds of hanging up.",
                  cls="meta"),
                cls="empty section",
            )
        else:
            body = Div(*[_render_card(r) for r in rows])

        return _page("Call Intake", nav, body)

    @rt("/toky_call_intake/{callid}")
    def intake_detail(request: Request, callid: str):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)

        with _conn() as conn:
            call = conn.execute("SELECT * FROM toky_calls WHERE callid = ?", (callid,)).fetchone()
            if not call:
                return _page("Not found", Div(P(f"Call {callid} not found."), cls="section"))
            transcript = conn.execute(
                "SELECT transcript_text, duration_s FROM toky_transcripts WHERE callid = ?", (callid,),
            ).fetchone()
            extract = conn.execute(
                "SELECT extract_json FROM toky_extracts WHERE callid = ?", (callid,),
            ).fetchone()
            cs_tasks = conn.execute(
                "SELECT * FROM toky_cs_tasks WHERE callid = ? ORDER BY created_at DESC", (callid,),
            ).fetchall()
            drafts = conn.execute(
                "SELECT * FROM toky_staging_drafts WHERE callid = ? ORDER BY created_at DESC", (callid,),
            ).fetchall()

        ex = {}
        if extract and extract["extract_json"]:
            try:
                ex = json.loads(extract["extract_json"])
            except json.JSONDecodeError:
                ex = {}

        header = Div(
            A("← Back", href="/toky_call_intake", cls="meta"),
            H2(ex.get("summary") or "(no summary)", style="margin-top:8px;"),
            Div(
                Span((ex.get("call_type") or "?").replace("_", " "),
                     cls=f"badge {ex.get('call_type') or 'other'}"),
                Span(f"confidence {ex.get('confidence', 0):.0%}" if ex.get("confidence") else "",
                     cls="meta", style="margin-left:8px;"),
                style="margin-top:6px;",
            ),
            cls="section",
        )

        # Meta
        meta = Div(
            H2("Call"),
            Div(
                NotStr(f"<dt>callid</dt><dd><code>{call['callid']}</code></dd>"),
                NotStr(f"<dt>direction</dt><dd>{call['direction']}</dd>"),
                NotStr(f"<dt>agent</dt><dd>{call['agent_id']}</dd>"),
                NotStr(f"<dt>from</dt><dd>{call['from_number']}</dd>"),
                NotStr(f"<dt>to</dt><dd>{call['to_number']}</dd>"),
                NotStr(f"<dt>duration</dt><dd>{_fmt_dur(call['duration_s'])}</dd>"),
                NotStr(f"<dt>started</dt><dd>{_fmt_dt(call['init_dt'])}</dd>"),
                NotStr(f"<dt>processing</dt><dd>{call['proc_status'] if 'proc_status' in call.keys() else call['status']}</dd>"),
                cls="kv",
            ),
            cls="section",
        )

        # Customer / property
        cust = ex.get("customer") if isinstance(ex.get("customer"), dict) else {}
        prop = ex.get("property") if isinstance(ex.get("property"), dict) else {}
        cust_prop = Div(
            H2("Customer & property"),
            Div(
                NotStr(f"<dt>name</dt><dd>{cust.get('name', '—')}</dd>"),
                NotStr(f"<dt>phone</dt><dd>{cust.get('phone', '—')}</dd>"),
                NotStr(f"<dt>email</dt><dd>{cust.get('email', '—')}</dd>"),
                NotStr(f"<dt>address</dt><dd>{prop.get('address', '—')}</dd>"),
                NotStr(f"<dt>property type</dt><dd>{prop.get('property_type', '—')}</dd>"),
                NotStr(f"<dt>occupancy</dt><dd>{prop.get('occupancy', '—')}</dd>"),
                NotStr(f"<dt>rooms</dt><dd>{', '.join(prop.get('rooms_discussed') or []) or '—'}</dd>"),
                cls="kv",
            ),
            cls="section",
        )

        # Key points & action items
        kp = ex.get("key_points") or []
        ai = ex.get("action_items") or []
        notes_section = None
        if kp or ai:
            rows_notes = []
            if kp:
                rows_notes.append(H3("Key points", style="font-size:13px;color:var(--muted);margin:0 0 4px;"))
                rows_notes.append(NotStr("<ul>" + "".join(f"<li>{k}</li>" for k in kp) + "</ul>"))
            if ai:
                rows_notes.append(H3("Action items", style="font-size:13px;color:var(--muted);margin:8px 0 4px;"))
                rows_notes.append(NotStr("<ul>" + "".join(f"<li>{a}</li>" for a in ai) + "</ul>"))
            notes_section = Div(*rows_notes, cls="section")

        # CS tasks
        cs_section = None
        if cs_tasks:
            parts = [H2("Customer-service tasks")]
            for t in cs_tasks:
                action = Form(
                    Button("Resolve", cls="btn btn-primary", type="submit"),
                    method="post",
                    action=f"/toky_call_intake/cs/{t['id']}/resolve",
                    style="display:inline;margin-left:8px;",
                ) if t["status"] == "open" else Form(
                    Button("Reopen", cls="btn", type="submit"),
                    method="post",
                    action=f"/toky_call_intake/cs/{t['id']}/reopen",
                    style="display:inline;margin-left:8px;",
                )
                parts.append(Div(
                    Div(
                        Span((t["severity"] or "normal"), cls=f"badge {t['severity'] or 'normal'}"),
                        Span(f" {t['status']}", cls="meta", style="margin-left:6px;"),
                        Span(" callback: ", cls="meta", style="margin-left:10px;"),
                        Span(t["callback_number"] or "—"),
                        action,
                    ),
                    H3(t["title"] or "(untitled)", style="margin:8px 0 4px;"),
                    P(t["description"] or "", cls="meta"),
                    style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-top:8px;",
                ))
            cs_section = Div(*parts, cls="section")

        # Staging drafts
        draft_section = None
        if drafts:
            parts = [H2("Staging project drafts")]
            for d in drafts:
                rooms = json.loads(d["rooms_discussed_json"] or "[]")
                lines = json.loads(d["quote_lines_json"] or "[]")
                actions = (
                    Form(
                        Button("Approve", cls="btn btn-primary", type="submit"),
                        method="post",
                        action=f"/toky_call_intake/draft/{d['id']}/approve",
                        style="display:inline;",
                    ),
                    Form(
                        Button("Reject", cls="btn btn-danger", type="submit"),
                        method="post",
                        action=f"/toky_call_intake/draft/{d['id']}/reject",
                        style="display:inline;margin-left:6px;",
                    ),
                ) if d["status"] == "draft" else (Span(f"status: {d['status']}", cls="meta"),)
                parts.append(Div(
                    Div(
                        Span(d["status"], cls="badge low" if d["status"] == "rejected" else "badge sales_follow_up"),
                        Span(f"  {d['customer_name'] or ''}  {d['customer_phone'] or ''}", cls="meta"),
                    ),
                    Div(
                        NotStr(f"<dt>address</dt><dd>{d['property_address'] or '—'}</dd>"),
                        NotStr(f"<dt>type</dt><dd>{d['property_type'] or '—'}</dd>"),
                        NotStr(f"<dt>rooms</dt><dd>{', '.join(rooms) or '—'}</dd>"),
                        NotStr(f"<dt>next step</dt><dd>{d['next_step'] or '—'}</dd>"),
                        NotStr(f"<dt>zoho match</dt><dd>{d['zoho_match_hint'] or '—'}</dd>"),
                        cls="kv",
                        style="margin-top:8px;",
                    ),
                    (Div(
                        Span("Quote lines:", cls="meta"),
                        NotStr("<ul>" + "".join(
                            f"<li>{line.get('item_name', '?')} × {line.get('quantity', 1)} — {line.get('area', '?')}</li>"
                            for line in lines
                        ) + "</ul>"),
                    ) if lines else ""),
                    Div(*actions, style="margin-top:10px;"),
                    style="padding:10px;border:1px solid var(--border);border-radius:8px;margin-top:8px;",
                ))
            draft_section = Div(*parts, cls="section")

        transcript_section = None
        if transcript and transcript["transcript_text"]:
            transcript_section = Div(
                H2("Transcript"),
                Div(transcript["transcript_text"], cls="transcript"),
                cls="section",
            )

        sections = [header, meta, cust_prop]
        if notes_section: sections.append(notes_section)
        if cs_section: sections.append(cs_section)
        if draft_section: sections.append(draft_section)
        if transcript_section: sections.append(transcript_section)

        return _page(f"Call {callid[:8]}", *sections)

    @rt("/toky_analytics")
    def analytics(request: Request):
        """Render the Opus analytics report (500-call Workstream A signal)."""
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)

        # Rough stats strip at the top
        with _conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM toky_calls").fetchone()[0]
            by_type_rows = conn.execute(
                "SELECT call_type, COUNT(*) FROM toky_extracts GROUP BY call_type ORDER BY 2 DESC"
            ).fetchall()
            cs_open = conn.execute("SELECT COUNT(*) FROM toky_cs_tasks WHERE status='open'").fetchone()[0]
            drafts_pending = conn.execute("SELECT COUNT(*) FROM toky_staging_drafts WHERE status='draft'").fetchone()[0]

        stats = Div(
            Div(
                Div(Span(f"{total}"), " calls indexed", cls="stat"),
                Div(Span(f"{cs_open}"), " CS open", cls="stat"),
                Div(Span(f"{drafts_pending}"), " drafts to review", cls="stat"),
                cls="stats-row",
            ),
            Div(
                *[Span(
                    f"{(ct or '—').replace('_',' ')}: ", Span(str(n), cls="strong"),
                    cls="pill",
                ) for ct, n in by_type_rows],
                style="margin-top:8px;",
            ),
            cls="section",
        )

        report_html = _render_analytics_report()
        body = Div(
            A("← Back to Call Intake", href="/toky_call_intake", cls="meta"),
            cls="section",
            style="padding:8px 16px;",
        )

        return _page(
            "Analytics",
            Style("""
                .stats-row { display:flex; gap:18px; flex-wrap:wrap; }
                .stat { font-size:13px; color:var(--muted); }
                .stat span { font-size:22px; font-weight:700; color:var(--text); margin-right:4px; }
                .pill .strong { font-weight:700; color:var(--text); }
                .report table { border-collapse:collapse; width:100%; font-size:13.5px; margin:10px 0; }
                .report th, .report td { border:1px solid var(--border); padding:6px 10px; text-align:left; }
                .report th { background:#f6f8fa; font-weight:600; }
                .report h1 { font-size:22px; margin:20px 0 8px; }
                .report h2 { font-size:17px; margin:18px 0 8px; padding-top:12px; border-top:1px solid var(--border); }
                .report h3 { font-size:14px; margin:14px 0 4px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
                .report blockquote { border-left:3px solid var(--accent); margin:8px 0; padding:4px 12px; color:#374151; background:#f9fafb; border-radius:0 6px 6px 0; font-style:italic; }
                .report code { background:#f3f4f6; padding:1px 5px; border-radius:3px; font-size:12.5px; }
                .report ul, .report ol { margin:6px 0; padding-left:24px; line-height:1.6; }
                .report hr { border:0; border-top:1px solid var(--border); margin:20px 0; }
                .tablewrap { overflow-x:auto; }
            """),
            body,
            stats,
            Div(NotStr(report_html), cls="section report"),
        )

    @rt("/toky_call_intake/cs/{task_id}/resolve", methods=["POST"])
    async def cs_resolve(request: Request, task_id: str):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)
        with _conn() as c:
            c.execute(
                "UPDATE toky_cs_tasks SET status = 'resolved', resolved_at = ?, assignee = COALESCE(assignee, ?) "
                "WHERE id = ?",
                (datetime.utcnow().isoformat(), user.get("email") if isinstance(user, dict) else str(user), task_id),
            )
            callid = c.execute("SELECT callid FROM toky_cs_tasks WHERE id = ?", (task_id,)).fetchone()
            c.commit()
        dest = f"/toky_call_intake/{callid[0]}" if callid else "/toky_call_intake"
        return RedirectResponse(dest, status_code=303)

    @rt("/toky_call_intake/cs/{task_id}/reopen", methods=["POST"])
    async def cs_reopen(request: Request, task_id: str):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)
        with _conn() as c:
            c.execute("UPDATE toky_cs_tasks SET status = 'open', resolved_at = NULL WHERE id = ?", (task_id,))
            callid = c.execute("SELECT callid FROM toky_cs_tasks WHERE id = ?", (task_id,)).fetchone()
            c.commit()
        dest = f"/toky_call_intake/{callid[0]}" if callid else "/toky_call_intake"
        return RedirectResponse(dest, status_code=303)

    @rt("/toky_call_intake/draft/{draft_id}/approve", methods=["POST"])
    async def draft_approve(request: Request, draft_id: str):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)
        with _conn() as c:
            c.execute(
                "UPDATE toky_staging_drafts SET status = 'approved', approved_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), draft_id),
            )
            callid = c.execute("SELECT callid FROM toky_staging_drafts WHERE id = ?", (draft_id,)).fetchone()
            c.commit()
        dest = f"/toky_call_intake/{callid[0]}" if callid else "/toky_call_intake"
        return RedirectResponse(dest, status_code=303)

    @rt("/toky_call_intake/draft/{draft_id}/reject", methods=["POST"])
    async def draft_reject(request: Request, draft_id: str):
        user = _current_user(request)
        if not user:
            return RedirectResponse("/signin", status_code=302)
        with _conn() as c:
            c.execute("UPDATE toky_staging_drafts SET status = 'rejected' WHERE id = ?", (draft_id,))
            callid = c.execute("SELECT callid FROM toky_staging_drafts WHERE id = ?", (draft_id,)).fetchone()
            c.commit()
        dest = f"/toky_call_intake/{callid[0]}" if callid else "/toky_call_intake"
        return RedirectResponse(dest, status_code=303)
