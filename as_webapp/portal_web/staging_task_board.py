"""
Staging Task Board — FastHTML port of Zoho's Staging_Task_Board page.

Reads from data/zoho_sync.db.Staging_Report (Zoho snapshot; auto-sync is
paused during UI-design phase — see project_sync_intervals_to_restore memory).

Field updates write straight to Staging_Report. No Zoho push; changes stay
local so web/iOS/Android all see each other. When Zoho is deprecated,
zoho_sync.db becomes the primary DB and these writes become authoritative.

Pattern for row buttons: an HTML form POSTs to a local handler, handler
writes the field, then 303 redirects back. Sub-pages not yet ported land
on /stub; see as_webapp/UNPORTED_PAGES.md for the queue.
"""
from datetime import date, datetime, timedelta
import json
import os
import sqlite3
from urllib.parse import urlencode

from fasthtml.common import (
    A, Body, Button, Dialog, Div, Form, H1, H2, H3, Head, Html, Input,
    Label, Li, Link, Main, Meta, Ol, P, Script, Span, Style, Svg, Table,
    Tbody, Td, Th, Thead, Tr, Titled, Title, Ul, NotStr,
)
from starlette.responses import HTMLResponse
from fasthtml.common import to_xml
from starlette.requests import Request
from starlette.responses import RedirectResponse


ZOHO_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "zoho_sync.db",
)

# Fields the "Mark as done today" buttons are allowed to set. Mirrors the
# Zoho page's whitelist at Staging_Manager.ds:18109+.
_DATE_FIELDS = {
    "Before_Picture_Upload_Date",
    "After_Picture_Upload_Date",
    "WhatsApp_Group_Created_Date",
    "Design_Items_Matched_Date",
    "Staging_Furniture_Design_Finish_Date",
    "Staging_Accessories_Packing_Finish_Date",
    "Check_Basement_Furniture_Size_Date",
    "Next_Steps_Email_Sent_Date",
    "Extension_Email_Sent_Date",
    "Staging_Completion_Confirmation_Sent_Date",
    "Destaging_Completion_Confirmation_Sent_Date",
    "Staging_Review_Request_Sent_Date",
    "Destaging_Review_Request_Sent_Date",
    "Invoice_Sent_Date",
    "Consultation_Confirmation_Email_Sent_Date",
    "Destaging_Confirmation_Email_Sent_Date",
}

_PERIOD_RANGES = {
    "today_only": lambda today: (today, today + timedelta(days=1)),
    "this_week":  lambda today: (today + timedelta(days=-5), today + timedelta(days=14)),
    "anytime":    lambda today: (today + timedelta(days=-1000), today + timedelta(days=365)),
}


# -------------------- data helpers --------------------

def _conn():
    c = sqlite3.connect(ZOHO_DB)
    c.row_factory = sqlite3.Row
    return c


def _parse_mdy(s):
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except Exception:
        return None


def _fmt_mdy(d): return d.strftime("%m/%d/%Y")


def _parse_people(s):
    if not s or not s.strip():
        return []
    try:
        arr = json.loads(s)
        return [p.get("display_value", "") for p in arr if isinstance(p, dict) and p.get("display_value")]
    except Exception:
        return []


def _parse_link(s):
    if not s or not s.strip():
        return None
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj.get("display_value")
    except Exception:
        pass
    return None


def _money(s):
    try:
        return float(s or 0)
    except Exception:
        return 0.0


def _fetch_stagings(period, show_my, show_stars, my_name):
    today = date.today()
    from_d, to_d = _PERIOD_RANGES.get(period, _PERIOD_RANGES["this_week"])(today)

    iso = ("substr(Coming_Staging_Destaging_Date, 7, 4) || '-' || "
           "substr(Coming_Staging_Destaging_Date, 1, 2) || '-' || "
           "substr(Coming_Staging_Destaging_Date, 4, 2)")

    sql = f"""
        SELECT *
        FROM Staging_Report
        WHERE (_sync_status IS NULL OR _sync_status != 'deleted')
          AND (Staging_Status = 'Active' OR Staging_Status = 'Inquired')
          AND Coming_Staging_Destaging_Date IS NOT NULL
          AND Coming_Staging_Destaging_Date != ''
          AND {iso} >= ?
          AND {iso} < ?
        ORDER BY {iso} ASC, CAST(ID AS INTEGER) ASC
        LIMIT 1000
    """
    with _conn() as c:
        rows = c.execute(sql, (from_d.isoformat(), to_d.isoformat())).fetchall()

    if show_my and my_name:
        needle = my_name.lower()
        rows = [r for r in rows if _is_mine(r, needle)]
    return rows, from_d, to_d, today


def _is_mine(row, needle):
    for field in (row["Stager"], row["Staging_Movers"], row["Destaging_Movers"]):
        for name in _parse_people(field):
            if name and needle in name.lower():
                return True
    return False


def _group_by_date(rows):
    out, current, group = [], None, []
    for r in rows:
        key = r["Coming_Staging_Destaging_Date"]
        if key != current:
            if group:
                out.append((current, group))
            current = key
            group = []
        group.append(r)
    if group:
        out.append((current, group))
    return out


# -------------------- theme system --------------------

# Six curated themes. Each defines an accent palette; base neutrals come
# from the root :root selector. Applied via <html data-theme="X">.
_THEMES = [
    ("default", "Slate", "#4f46e5"),   # indigo
    ("ocean",   "Ocean", "#0891b2"),   # cyan/teal
    ("forest",  "Forest", "#059669"),  # emerald
    ("sunset",  "Sunset", "#ea580c"),  # orange
    ("rose",    "Rose",  "#e11d48"),   # rose/red
    ("noir",    "Noir",  "#0a0a0a"),   # grayscale / high contrast
]


def _style_block():
    return Style("""
    /* ---------- reset + base ---------- */
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; height: 100%; }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11', 'ss01';
        background: var(--bg);
        color: var(--text);
        font-size: 14px;
        line-height: 1.45;
        -webkit-font-smoothing: antialiased;
        transition: background 180ms ease, color 180ms ease;
    }

    /* ---------- theme: light defaults ---------- */
    :root {
        --bg:            #f6f7fb;
        --surface:       #ffffff;
        --surface-2:     #f1f3f9;
        --surface-3:     #e7eaf3;
        --border:        #e3e6ef;
        --border-strong: #c9cfdd;
        --text:          #181b2b;
        --text-muted:    #5b6275;
        --text-faint:    #8b91a5;

        --accent:        #4f46e5;
        --accent-hover:  #4338ca;
        --accent-soft:   #eef0ff;
        --accent-fg:     #ffffff;

        --success:       #059669;
        --success-soft:  #d1fae5;
        --warning:       #d97706;
        --warning-soft:  #fef3c7;
        --danger:        #dc2626;
        --danger-soft:   #fee2e2;

        --row-odd:       #ffffff;
        --row-even:      #fafbfd;
        --row-hover:     #f4f6fb;
        --row-today:     #eff6ff;
        --row-destage:   #fffbeb;
        --row-inquired:  #f3f4f8;
        --row-inactive:  #eeeef2;

        --date-bg:       linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        --date-text:     #78350f;
        --date-border:   #fbbf24;

        --shadow-sm: 0 1px 2px rgba(15,23,42,.06);
        --shadow-md: 0 4px 12px rgba(15,23,42,.08);
        --shadow-lg: 0 12px 32px rgba(15,23,42,.12);

        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 16px;

        --toolbar-h: 64px;
    }

    /* ---------- theme accents (override accent family) ---------- */
    :root[data-theme="ocean"]  { --accent:#0891b2; --accent-hover:#0e7490; --accent-soft:#ecfeff; }
    :root[data-theme="forest"] { --accent:#059669; --accent-hover:#047857; --accent-soft:#ecfdf5; }
    :root[data-theme="sunset"] { --accent:#ea580c; --accent-hover:#c2410c; --accent-soft:#fff7ed; }
    :root[data-theme="rose"]   { --accent:#e11d48; --accent-hover:#be123c; --accent-soft:#fff1f2; }
    :root[data-theme="noir"]   { --accent:#0a0a0a; --accent-hover:#000000; --accent-soft:#f4f4f5; }

    /* ---------- dark mode (system or forced) ---------- */
    @media (prefers-color-scheme: dark) {
        :root:not([data-mode="light"]) {
            --bg:            #0b0d14;
            --surface:       #141726;
            --surface-2:     #1c2033;
            --surface-3:     #252a42;
            --border:        #262a3f;
            --border-strong: #363b58;
            --text:          #e6e8ef;
            --text-muted:    #9ea5bd;
            --text-faint:    #6b7490;

            --accent:        #818cf8;
            --accent-hover:  #a5b4fc;
            --accent-soft:   #1e1f3a;

            --success:       #34d399;
            --success-soft:  #0f2921;
            --warning:       #fbbf24;
            --warning-soft:  #2a2110;
            --danger:        #f87171;
            --danger-soft:   #2a1515;

            --row-odd:       #141726;
            --row-even:      #181c2f;
            --row-hover:     #1e2337;
            --row-today:     #1a2344;
            --row-destage:   #231a0d;
            --row-inquired:  #171a28;
            --row-inactive:  #111320;

            --date-bg:       linear-gradient(135deg, #2a1f0a 0%, #3a2a0d 100%);
            --date-text:     #fbbf24;
            --date-border:   #d97706;

            --shadow-sm: 0 1px 2px rgba(0,0,0,.3);
            --shadow-md: 0 4px 12px rgba(0,0,0,.35);
            --shadow-lg: 0 16px 40px rgba(0,0,0,.5);
        }
        :root:not([data-mode="light"])[data-theme="ocean"]  { --accent:#22d3ee; --accent-hover:#67e8f9; --accent-soft:#0a2830; }
        :root:not([data-mode="light"])[data-theme="forest"] { --accent:#34d399; --accent-hover:#6ee7b7; --accent-soft:#0f2921; }
        :root:not([data-mode="light"])[data-theme="sunset"] { --accent:#fb923c; --accent-hover:#fdba74; --accent-soft:#2a1a0a; }
        :root:not([data-mode="light"])[data-theme="rose"]   { --accent:#fb7185; --accent-hover:#fda4af; --accent-soft:#2a1015; }
        :root:not([data-mode="light"])[data-theme="noir"]   { --accent:#e5e5e5; --accent-hover:#fafafa; --accent-soft:#18181b; }
    }
    /* explicit dark mode toggle (overrides system preference) */
    :root[data-mode="dark"] {
        --bg:#0b0d14; --surface:#141726; --surface-2:#1c2033; --surface-3:#252a42;
        --border:#262a3f; --border-strong:#363b58;
        --text:#e6e8ef; --text-muted:#9ea5bd; --text-faint:#6b7490;
        --accent:#818cf8; --accent-hover:#a5b4fc; --accent-soft:#1e1f3a;
        --success:#34d399; --success-soft:#0f2921;
        --warning:#fbbf24; --warning-soft:#2a2110;
        --danger:#f87171; --danger-soft:#2a1515;
        --row-odd:#141726; --row-even:#181c2f; --row-hover:#1e2337;
        --row-today:#1a2344; --row-destage:#231a0d; --row-inquired:#171a28; --row-inactive:#111320;
        --date-bg: linear-gradient(135deg, #2a1f0a 0%, #3a2a0d 100%);
        --date-text:#fbbf24; --date-border:#d97706;
        --shadow-sm: 0 1px 2px rgba(0,0,0,.3);
        --shadow-md: 0 4px 12px rgba(0,0,0,.35);
        --shadow-lg: 0 16px 40px rgba(0,0,0,.5);
    }
    :root[data-mode="dark"][data-theme="ocean"]  { --accent:#22d3ee; --accent-hover:#67e8f9; --accent-soft:#0a2830; }
    :root[data-mode="dark"][data-theme="forest"] { --accent:#34d399; --accent-hover:#6ee7b7; --accent-soft:#0f2921; }
    :root[data-mode="dark"][data-theme="sunset"] { --accent:#fb923c; --accent-hover:#fdba74; --accent-soft:#2a1a0a; }
    :root[data-mode="dark"][data-theme="rose"]   { --accent:#fb7185; --accent-hover:#fda4af; --accent-soft:#2a1015; }
    :root[data-mode="dark"][data-theme="noir"]   { --accent:#e5e5e5; --accent-hover:#fafafa; --accent-soft:#18181b; }

    /* ---------- layout shell ---------- */
    .app-shell {
        display: flex; flex-direction: column;
        height: 100vh; overflow: hidden;
    }
    .toolbar {
        flex: 0 0 var(--toolbar-h);
        display: flex; align-items: center; gap: 12px;
        padding: 0 20px;
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        z-index: 10;
    }
    .toolbar-title {
        font-weight: 700; font-size: 17px; letter-spacing: -0.01em;
        margin-right: 8px;
    }
    .toolbar-title .accent { color: var(--accent); }
    .toolbar-spacer { flex: 1; }
    .toolbar-meta {
        font-size: 12px; color: var(--text-muted);
        padding: 4px 10px; background: var(--surface-2);
        border-radius: var(--radius-sm);
    }
    .seg {
        display: inline-flex; background: var(--surface-2);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        padding: 3px; gap: 2px;
    }
    .seg a, .seg button {
        padding: 6px 12px; font-size: 13px; font-weight: 500;
        color: var(--text-muted); border: 0; background: transparent;
        border-radius: 7px; cursor: pointer; text-decoration: none;
        transition: background 140ms ease, color 140ms ease;
    }
    .seg a:hover, .seg button:hover { color: var(--text); background: var(--surface-3); }
    .seg a.on, .seg button.on {
        background: var(--surface); color: var(--accent);
        box-shadow: var(--shadow-sm);
    }
    .toolbar-btn {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 7px 12px; font-size: 13px; font-weight: 500;
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        cursor: pointer; text-decoration: none;
        transition: all 140ms ease;
    }
    .toolbar-btn:hover { background: var(--surface-2); border-color: var(--border-strong); }
    .toolbar-btn.accent {
        background: var(--accent); color: var(--accent-fg); border-color: var(--accent);
    }
    .toolbar-btn.accent:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .toolbar-btn svg { width: 15px; height: 15px; }

    /* ---------- main scroll area ---------- */
    .scroll-area {
        flex: 1; overflow: auto; position: relative;
        background: var(--bg);
    }

    /* ---------- desktop table ---------- */
    table.board {
        width: 100%; border-collapse: separate; border-spacing: 0;
        background: var(--surface);
        font-size: 13px;
    }
    table.board thead tr {
        position: sticky; top: 0; z-index: 5;
        background: var(--surface-2);
    }
    table.board thead th {
        text-align: left; font-weight: 600; font-size: 12px;
        text-transform: uppercase; letter-spacing: 0.04em;
        color: var(--text-muted);
        padding: 12px 14px; border-bottom: 1px solid var(--border);
        white-space: nowrap;
    }
    table.board tbody td {
        padding: 14px; vertical-align: top;
        border-bottom: 1px solid var(--border);
        min-width: 240px; max-width: 340px;
    }
    table.board tbody td.col-wide { min-width: 280px; max-width: 420px; }
    table.board tbody td.col-narrow { min-width: 180px; max-width: 220px; }

    tr.data-row td { background: var(--row-odd); transition: background 120ms ease; }
    tr.data-row:nth-child(even) td { background: var(--row-even); }
    tr.data-row:hover td { background: var(--row-hover); }
    tr.data-row.state-today td { background: var(--row-today); }
    tr.data-row.state-destage td { background: var(--row-destage); }
    tr.data-row.state-inquired td { background: var(--row-inquired); }
    tr.data-row.state-inactive td { background: var(--row-inactive); color: var(--text-muted); }

    /* full-width date banner row */
    tr.date-banner td {
        background: var(--date-bg);
        color: var(--date-text);
        font-weight: 700; font-size: 13px;
        text-transform: uppercase; letter-spacing: 0.08em;
        text-align: center; padding: 10px;
        border-top: 2px solid var(--date-border);
        border-bottom: 1px solid var(--date-border);
        position: sticky; top: 41px; z-index: 4;
    }
    tr.slot-row td {
        font-size: 12px; color: var(--text-faint);
        font-style: italic; text-align: center; padding: 8px;
        background: var(--surface);
    }

    /* ---------- row cell content ---------- */
    .staging-title { font-weight: 700; font-size: 14px; color: var(--text); margin-bottom: 4px; }
    .staging-meta { color: var(--text-muted); font-size: 12px; margin-bottom: 2px; }
    .staging-address { font-weight: 600; color: var(--text); margin-top: 2px; }
    .staging-address + .staging-meta { margin-top: 2px; }
    .sublinks {
        display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;
    }
    .sublink {
        font-size: 11px; font-weight: 500;
        padding: 3px 8px; border-radius: var(--radius-sm);
        background: var(--accent-soft); color: var(--accent);
        text-decoration: none; transition: background 140ms ease;
    }
    .sublink:hover { background: var(--accent); color: var(--accent-fg); }

    /* milestone chips */
    .chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px; font-size: 11px; font-weight: 500;
        background: var(--surface-2); color: var(--text-muted);
        border: 1px solid var(--border); border-radius: 999px;
        cursor: pointer; transition: all 140ms ease;
    }
    .chip:hover { background: var(--surface-3); color: var(--text); }
    .chip.done {
        background: var(--success-soft); color: var(--success);
        border-color: transparent;
    }
    .chip svg { width: 10px; height: 10px; }
    .chip-form { display: inline-block; margin: 0; padding: 0; }
    .chip-btn {
        all: unset; display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px; font-size: 11px; font-weight: 500; line-height: 1;
        background: var(--surface-2); color: var(--text-muted);
        border: 1px solid var(--border); border-radius: 999px;
        cursor: pointer; transition: all 140ms ease; font-family: inherit;
    }
    .chip-btn:hover { background: var(--surface-3); color: var(--text); }
    .chip-btn.done { background: var(--success-soft); color: var(--success); border-color: transparent; }

    /* action buttons (Download Invoice, etc.) */
    .btn {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 10px; font-size: 12px; font-weight: 500;
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-sm);
        cursor: pointer; text-decoration: none; font-family: inherit;
        transition: all 140ms ease;
    }
    .btn:hover { background: var(--surface-2); border-color: var(--border-strong); }
    .btn.primary { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
    .btn.primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .btn-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }

    /* money display */
    .money-block { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; font-size: 12px; }
    .money-block .label { color: var(--text-muted); }
    .money-block .val { font-variant-numeric: tabular-nums; font-weight: 500; }
    .money-block .val.owing { color: var(--danger); font-weight: 600; }

    /* notes column */
    .notes { font-size: 12px; color: var(--text-muted); line-height: 1.5; max-height: 260px; overflow-y: auto; }

    /* persons column */
    .persons { font-size: 12px; }
    .persons .row { margin-bottom: 4px; }
    .persons .label { color: var(--text-faint); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; margin-right: 4px; }
    .persons .val { color: var(--text); font-weight: 500; }

    /* ---------- mobile card layout ---------- */
    .cards { padding: 16px; display: flex; flex-direction: column; gap: 12px; max-width: 900px; margin: 0 auto; }
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: 16px;
        transition: box-shadow 180ms ease;
    }
    .card:hover { box-shadow: var(--shadow-md); }
    .card.today { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-soft); }
    .card-date-banner {
        font-size: 12px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; color: var(--date-text);
        padding: 10px 16px; background: var(--date-bg);
        border: 1px solid var(--date-border);
        border-radius: var(--radius-md);
        text-align: center; margin-top: 8px;
    }
    .card .staging-title { font-size: 15px; }

    /* ---------- modal ---------- */
    dialog.modal {
        border: 0; padding: 0; background: transparent;
        max-width: min(520px, 92vw); width: 100%;
    }
    dialog.modal::backdrop { background: rgba(15,23,42,.5); backdrop-filter: blur(4px); }
    dialog.modal .modal-card {
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg); padding: 24px;
        max-height: 85vh; overflow-y: auto;
    }
    .modal-title { font-size: 18px; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.01em; }
    .modal-sub { font-size: 13px; color: var(--text-muted); margin: 0 0 20px; }
    .modal-section { margin-top: 20px; }
    .modal-section h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 0 0 10px; }

    .theme-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .theme-card {
        position: relative; padding: 12px; cursor: pointer;
        border: 2px solid var(--border); border-radius: var(--radius-md);
        background: var(--surface); transition: all 140ms ease;
        text-align: left;
    }
    .theme-card:hover { border-color: var(--border-strong); }
    .theme-card.active { border-color: var(--accent); background: var(--accent-soft); }
    .theme-swatch {
        display: block; height: 32px; border-radius: var(--radius-sm);
        margin-bottom: 8px; background: var(--sw, #4f46e5);
    }
    .theme-name { font-size: 12px; font-weight: 600; color: var(--text); }
    .theme-card .check { display: none; }
    .theme-card.active .check {
        position: absolute; top: 6px; right: 6px;
        width: 18px; height: 18px; border-radius: 999px;
        background: var(--accent); color: var(--accent-fg);
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700; line-height: 1;
    }

    .mode-seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 3px; gap: 2px; }
    .mode-seg button {
        padding: 7px 14px; font-size: 13px; font-weight: 500;
        background: transparent; color: var(--text-muted);
        border: 0; border-radius: 7px; cursor: pointer;
        display: inline-flex; align-items: center; gap: 6px;
        font-family: inherit;
    }
    .mode-seg button:hover { color: var(--text); }
    .mode-seg button.on { background: var(--surface); color: var(--accent); box-shadow: var(--shadow-sm); }
    .mode-seg svg { width: 14px; height: 14px; }

    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 24px; }

    /* ---------- stub page ---------- */
    .stub-wrap { max-width: 560px; margin: 80px auto; padding: 0 20px; }
    .stub-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 32px; box-shadow: var(--shadow-md); }
    .stub-card h1 { margin: 0 0 8px; font-size: 22px; letter-spacing: -0.02em; }
    .stub-card .pill { display: inline-block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--warning); background: var(--warning-soft); padding: 3px 10px; border-radius: 999px; margin-bottom: 14px; }
    .stub-card .params { list-style: none; padding: 0; margin: 16px 0; background: var(--surface-2); border-radius: var(--radius-md); padding: 12px; font-family: 'SF Mono', Menlo, monospace; font-size: 12px; }
    .stub-card .params li { padding: 2px 0; color: var(--text); }
    .stub-card .params li span { color: var(--text-muted); }

    /* scrollbar styling */
    .scroll-area::-webkit-scrollbar, .modal-card::-webkit-scrollbar, .notes::-webkit-scrollbar { width: 10px; height: 10px; }
    .scroll-area::-webkit-scrollbar-thumb, .modal-card::-webkit-scrollbar-thumb, .notes::-webkit-scrollbar-thumb {
        background: var(--border-strong); border-radius: 5px; border: 2px solid var(--bg);
    }
    .scroll-area::-webkit-scrollbar-track { background: transparent; }

    /* responsive toolbar collapse */
    @media (max-width: 780px) {
        .toolbar { flex-wrap: wrap; height: auto; padding: 12px; gap: 8px; }
        .app-shell { height: 100vh; }
        .toolbar-title { flex: 1 0 100%; }
        :root { --toolbar-h: auto; }
        table.board thead th, table.board tbody td { padding: 10px; }
        .theme-grid { grid-template-columns: repeat(2, 1fr); }
    }
    """)


def _script_block():
    # Tiny theme controller: reads localStorage on load, writes on change.
    return Script(r"""
    (function() {
        const doc = document.documentElement;
        const THEME_KEY = 'tb_theme';
        const MODE_KEY = 'tb_mode';

        function apply() {
            const theme = localStorage.getItem(THEME_KEY) || 'default';
            const mode = localStorage.getItem(MODE_KEY) || 'auto';
            if (theme === 'default') doc.removeAttribute('data-theme');
            else doc.setAttribute('data-theme', theme);
            if (mode === 'auto') doc.removeAttribute('data-mode');
            else doc.setAttribute('data-mode', mode);
        }
        apply();

        window.TB = {
            setTheme(t) { localStorage.setItem(THEME_KEY, t); apply(); refreshModalState(); },
            setMode(m) { localStorage.setItem(MODE_KEY, m); apply(); refreshModalState(); },
            openModal() {
                const dlg = document.getElementById('theme-modal');
                if (dlg && dlg.showModal) { refreshModalState(); dlg.showModal(); }
            },
            closeModal() {
                const dlg = document.getElementById('theme-modal');
                if (dlg && dlg.close) dlg.close();
            },
        };

        function refreshModalState() {
            const theme = localStorage.getItem(THEME_KEY) || 'default';
            const mode = localStorage.getItem(MODE_KEY) || 'auto';
            document.querySelectorAll('.theme-card').forEach(el => {
                el.classList.toggle('active', el.dataset.theme === theme);
            });
            document.querySelectorAll('.mode-seg button').forEach(el => {
                el.classList.toggle('on', el.dataset.mode === mode);
            });
        }

        // backdrop-click to close
        document.addEventListener('click', e => {
            const dlg = document.getElementById('theme-modal');
            if (dlg && dlg.open && e.target === dlg) dlg.close();
        });
    })();
    """)


# -------------------- SVG icons --------------------

def _icon(d, size=15):
    """Inline SVG from a path `d`. Uses currentColor so it inherits text color."""
    return NotStr(
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round"><path d="{d}"/></svg>'
    )


_ICON_CHECK = "M20 6L9 17l-5-5"
_ICON_PALETTE = "M12 22a10 10 0 1 1 0-20 10 10 0 0 1 10 10c0 3-2 3-4 3h-2a2 2 0 0 0-2 2v2a2 2 0 0 1-2 2z"
_ICON_SUN = "M12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10z M12 1v2 M12 21v2 M4.22 4.22l1.42 1.42 M18.36 18.36l1.42 1.42 M1 12h2 M21 12h2 M4.22 19.78l1.42-1.42 M18.36 5.64l1.42-1.42"
_ICON_MOON = "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
_ICON_MONITOR = "M3 3h18v12H3z M8 21h8 M12 15v6"
_ICON_MOBILE = "M5 2h14v20H5z M12 18h.01"
_ICON_DESKTOP = "M3 4h18v12H3z M8 20h8 M12 16v4"


# -------------------- UI builders --------------------

def _modal():
    """Theme selector modal (native <dialog>)."""
    theme_cards = []
    for slug, name, swatch in _THEMES:
        theme_cards.append(
            Button(
                NotStr(f'<span class="check">✓</span>'),
                NotStr(f'<span class="theme-swatch" style="--sw:{swatch}"></span>'),
                NotStr(f'<span class="theme-name">{name}</span>'),
                type="button",
                cls="theme-card",
                **{"data-theme": slug, "onclick": f"TB.setTheme('{slug}')"},
            )
        )

    return Dialog(
        Div(
            H2("Appearance", cls="modal-title"),
            P("Pick a theme and color mode. Preferences stay on this device.", cls="modal-sub"),

            Div(
                H3("Theme"),
                Div(*theme_cards, cls="theme-grid"),
                cls="modal-section",
            ),

            Div(
                H3("Color mode"),
                Div(
                    Button(_icon(_ICON_MONITOR), Span(" Auto"), type="button",
                           cls="on", onclick="TB.setMode('auto')", **{"data-mode": "auto"}),
                    Button(_icon(_ICON_SUN), Span(" Light"), type="button",
                           onclick="TB.setMode('light')", **{"data-mode": "light"}),
                    Button(_icon(_ICON_MOON), Span(" Dark"), type="button",
                           onclick="TB.setMode('dark')", **{"data-mode": "dark"}),
                    cls="mode-seg",
                ),
                cls="modal-section",
            ),

            Div(
                Button("Done", type="button", cls="toolbar-btn accent", onclick="TB.closeModal()"),
                cls="modal-actions",
            ),
            cls="modal-card",
        ),
        id="theme-modal",
        cls="modal",
    )


def _toolbar(display_mode, period, show_my, rows_count, from_d, to_d, today):
    def link(params, label, on=False):
        qs = {
            "display": display_mode if display_mode != "desktop" else "",
            "show_period": period if period != "this_week" else "",
            "show_only_my_tasks": "yes" if show_my else "",
        }
        qs.update(params)
        qs = {k: v for k, v in qs.items() if v not in (None, "")}
        href = "/staging_task_board"
        if qs:
            href += "?" + urlencode(qs)
        return A(label, href=href, cls="on" if on else "")

    period_seg = Div(
        link({"show_period": "today_only"}, "Today", on=(period == "today_only")),
        link({"show_period": "this_week"}, "Week", on=(period == "this_week")),
        link({"show_period": "anytime"}, "All", on=(period == "anytime")),
        cls="seg",
    )
    mine_seg = Div(
        link({"show_only_my_tasks": ""}, "All tasks", on=(not show_my)),
        link({"show_only_my_tasks": "yes"}, "My tasks", on=show_my),
        cls="seg",
    )
    display_seg = Div(
        A(_icon(_ICON_DESKTOP), NotStr(" Desktop"),
          href="/staging_task_board" + (
              "?" + urlencode({k: v for k, v in {
                  "show_period": period if period != "this_week" else "",
                  "show_only_my_tasks": "yes" if show_my else "",
              }.items() if v}) if (period != "this_week" or show_my) else ""
          ),
          cls="on" if display_mode == "desktop" else ""),
        A(_icon(_ICON_MOBILE), NotStr(" Mobile"),
          href="/staging_task_board?" + urlencode({
              k: v for k, v in {
                  "display": "mobile",
                  "show_period": period if period != "this_week" else "",
                  "show_only_my_tasks": "yes" if show_my else "",
              }.items() if v
          }),
          cls="on" if display_mode == "mobile" else ""),
        cls="seg",
    )

    meta = Span(
        f"{rows_count} stagings · {from_d.strftime('%b %d')} → {(to_d - timedelta(days=1)).strftime('%b %d')}",
        cls="toolbar-meta",
    )

    theme_btn = Button(
        _icon(_ICON_PALETTE), Span(" Theme"),
        type="button", cls="toolbar-btn", onclick="TB.openModal()",
    )

    return Div(
        Div(NotStr("Staging "), Span("Task Board", cls="accent"), cls="toolbar-title"),
        period_seg,
        mine_seg,
        display_seg,
        Div(cls="toolbar-spacer"),
        meta,
        theme_btn,
        cls="toolbar",
    )


# -------------------- column content --------------------

def _sub_page_link(label, page, **params):
    q = {"page": page, **{k: v for k, v in params.items() if v}}
    return A(label, href="/stub?" + urlencode(q), target="_blank", cls="sublink")


def _chip_button(staging_id, field, label, done):
    return Form(
        Button(
            _icon(_ICON_CHECK, size=10) if done else NotStr("○ "),
            Span(label),
            type="submit", cls=f"chip-btn {'done' if done else ''}",
        ),
        Input(type="hidden", name="staging_id", value=staging_id),
        Input(type="hidden", name="field", value=field),
        method="POST", action="/staging_task_board/set_date",
        cls="chip-form",
    )


def _col_staging(row, serial):
    date_s = row["Coming_Staging_Destaging_Date"] or ""
    d = _parse_mdy(date_s)
    occ = row["Occupancy_Type"] or ""
    prop = row["Property_Type"] or ""
    sd = _parse_mdy(row["Staging_Date"])
    dd = _parse_mdy(row["Destaging_Date"])
    today = date.today()
    is_destage = dd and d == dd and (not sd or sd != dd)
    kind = "Destaging" if is_destage else "Staging"

    remaining_days = None
    if sd and dd:
        remaining_days = (dd - max(sd, today)).days if today >= sd else (dd - sd).days
    try:
        item_count = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        item_count = 0

    address = _parse_link(row["Staging_Address"]) or row["Staging_Display_Name"] or "—"
    eta = row["Staging_ETA"] or ""
    drive = row["Driving_Time"] or ""

    meta_bits = []
    if occ or prop:
        meta_bits.append(f"{occ} {prop}".strip())
    if eta:
        meta_bits.append(eta)
    if drive:
        meta_bits.append(f"{drive} min drive")

    return Td(
        Div(f"{kind} {serial}", cls="staging-title"),
        Div(f"{remaining_days if remaining_days is not None else '—'} days remaining · {item_count} items", cls="staging-meta"),
        Div(address, cls="staging-address"),
        *([Div(" · ".join(meta_bits), cls="staging-meta")] if meta_bits else []),
        Div(
            A("Edit", href=f"/stub?{urlencode({'page':'Staging_Edit','staging_id':row['ID']})}", cls="sublink"),
            _sub_page_link("Design", "Staging_Design", staging_id=row["ID"]),
            _sub_page_link("Pictures", "Staging_Videos_and_Pictures", staging_id=row["ID"]),
            _sub_page_link("Packing", "Packing_Guide_Page", staging_id=row["ID"], staging_type="Staging"),
            _sub_page_link("Setup", "Staging_Setup_Guide", staging_id=row["ID"]),
            cls="sublinks",
        ),
        cls="col-wide",
    )


def _col_persons(row):
    cust_fn = row["Customer_First_Name"] or ""
    cust_ln = row["Customer_Last_Name"] or ""
    customer = f"{cust_fn} {cust_ln}".strip() or "—"
    stagers = ", ".join(_parse_people(row["Stager"])) or "—"
    movers = ", ".join(_parse_people(row["Staging_Movers"])) or "—"
    destage = ", ".join(_parse_people(row["Destaging_Movers"]))

    rows = [
        Div(Span("Customer", cls="label"), Span(customer, cls="val"), cls="row"),
        Div(Span("Stager", cls="label"), Span(stagers, cls="val"), cls="row"),
        Div(Span("Movers", cls="label"), Span(movers, cls="val"), cls="row"),
    ]
    if destage:
        rows.append(Div(Span("Destage", cls="label"), Span(destage, cls="val"), cls="row"))

    return Td(Div(*rows, cls="persons"))


def _col_actions(row):
    sid = row["ID"]
    milestones = [
        ("Design", "Design_Items_Matched_Date"),
        ("Before", "Before_Picture_Upload_Date"),
        ("After", "After_Picture_Upload_Date"),
        ("Packing", "Staging_Accessories_Packing_Finish_Date"),
        ("Setup", "Staging_Furniture_Design_Finish_Date"),
        ("WhatsApp", "WhatsApp_Group_Created_Date"),
        ("Next Steps", "Next_Steps_Email_Sent_Date"),
        ("Basement", "Check_Basement_Furniture_Size_Date"),
    ]
    chips = []
    for label, field in milestones:
        val = row[field]
        done = bool(val and val.strip())
        chips.append(_chip_button(sid, field, label, done))
    return Td(Div(*chips, cls="chips"))


def _col_moving(row):
    text = (row["Staging_Moving_Instructions"] or "").strip()
    return Td(Div(NotStr(text.replace("\n", "<br>")) if text else Span("—", cls="staging-meta"), cls="notes"))


def _col_notes(row):
    notes = (row["General_Notes"] or "").strip()
    return Td(Div(NotStr(notes.replace("\n", "<br>")) if notes else Span("—", cls="staging-meta"), cls="notes"))


def _col_accounting(row):
    sid = row["ID"]
    total = _money(row["Total_Staging_Fee"])
    paid = _money(row["Paid_Amount"])
    owing = _money(row["Owing_Amount"])
    return Td(
        Div(
            Span("Fee", cls="label"), Span(f"${total:,.0f}", cls="val"),
            Span("Paid", cls="label"), Span(f"${paid:,.0f}", cls="val"),
            Span("Owing", cls="label"), Span(f"${owing:,.0f}", cls=f"val{' owing' if owing > 0 else ''}"),
            cls="money-block",
        ),
        Div(
            A("History", href=f"/stub?{urlencode({'page':'Payment_Report','staging_id':sid})}", target="_blank", cls="btn"),
            A("Invoice", href=f"/stub?{urlencode({'page':'Staging_Invoice','staging_id':sid})}", cls="btn"),
            A("Send", href=f"/stub?{urlencode({'page':'Email_Generator','staging_id':sid,'email_type':'Payment Notification'})}", cls="btn primary"),
            cls="btn-row",
        ),
        Div(
            _chip_button(sid, "Invoice_Sent_Date", "Invoice sent", bool(row["Invoice_Sent_Date"])),
            cls="chips", style="margin-top:6px",
        ),
    )


def _col_listing(row):
    sid = row["ID"]
    pics_folder = row["Pictures_Folder"] or ""
    mls = row["MLS"] or ""
    housesigma = row["HouseSigma_URL"] or ""

    children = []
    if pics_folder:
        children.append(A("📁 Drive folder", href=pics_folder, target="_blank", cls="btn"))
    children.append(
        Div(
            _chip_button(sid, "After_Picture_Upload_Date", "After pics up", bool(row["After_Picture_Upload_Date"])),
            cls="chips", style="margin-top:6px",
        )
    )
    if mls:
        children.append(Div(Span("MLS  ", cls="label"), Span(mls, cls="val"), cls="persons", style="margin-top:8px;font-size:12px"))
    if housesigma:
        children.append(A("HouseSigma ↗", href=housesigma, target="_blank", cls="btn", style="margin-top:6px"))
    children.append(
        A("Update MLS info",
          href=f"/stub?{urlencode({'page':'Staging_Edit','staging_id':sid,'focus':'MLS'})}",
          cls="btn", style="margin-top:6px")
    )
    return Td(Div(*children, cls="btn-row", style="flex-direction:column;align-items:flex-start"), cls="col-narrow")


def _row_state(row):
    today = date.today()
    status = (row["Staging_Status"] or "").lower()
    sd = _parse_mdy(row["Staging_Date"])
    dd = _parse_mdy(row["Destaging_Date"])
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])

    if status == "inquired":
        return "state-inquired"
    if dd and coming == dd:
        return "state-destage"
    if coming == today:
        return "state-today"
    return ""


def _desktop_table(grouped, from_d, to_d, today):
    headers = Thead(Tr(
        Th("Staging"), Th("Persons"), Th("Tasks"),
        Th("Moving Instructions"), Th("General Notes"),
        Th("Accounting"), Th("Listing"),
    ))

    by_date = {}
    for date_str, group in grouped:
        d = _parse_mdy(date_str)
        if d:
            by_date[d] = (date_str, group)

    body_rows = []
    d = from_d
    while d < to_d:
        if d in by_date:
            date_str, group = by_date[d]
            banner_text = d.strftime("%A · %B %-d, %Y")
            today_marker = "  (today)" if d == today else ""
            body_rows.append(Tr(
                Td(banner_text + today_marker, colspan="7"),
                cls="date-banner",
            ))
            for i, r in enumerate(group, start=1):
                body_rows.append(Tr(
                    _col_staging(r, i),
                    _col_persons(r),
                    _col_actions(r),
                    _col_moving(r),
                    _col_notes(r),
                    _col_accounting(r),
                    _col_listing(r),
                    cls=f"data-row {_row_state(r)}",
                ))
        elif d.weekday() < 5:
            body_rows.append(Tr(
                Td(d.strftime("%A · %B %-d, %Y") + "  (open)", colspan="7"),
                cls="date-banner",
            ))
            body_rows.append(Tr(
                Td("No stagings scheduled · 6 slots open", colspan="7"),
                cls="slot-row",
            ))
        d += timedelta(days=1)

    return Div(Table(headers, Tbody(*body_rows), cls="board"))


def _mobile_cards(grouped, from_d, to_d, today):
    items = []
    by_date = {_parse_mdy(k): (k, g) for k, g in grouped}
    by_date.pop(None, None)

    d = from_d
    while d < to_d:
        if d in by_date:
            date_str, group = by_date[d]
            items.append(Div(d.strftime("%A · %B %-d"), cls="card-date-banner"))
            for i, r in enumerate(group, start=1):
                is_today = d == today
                address = _parse_link(r["Staging_Address"]) or r["Staging_Display_Name"] or "—"
                stagers = ", ".join(_parse_people(r["Stager"])) or "—"
                movers = ", ".join(_parse_people(r["Staging_Movers"])) or "—"
                cust = f"{r['Customer_First_Name'] or ''} {r['Customer_Last_Name'] or ''}".strip() or "—"
                items.append(Div(
                    Div(f"Staging {i} · {r['Occupancy_Type'] or ''} {r['Property_Type'] or ''}".strip(" ·"), cls="staging-title"),
                    Div(address, cls="staging-address"),
                    Div(
                        Div(Span("Customer", cls="label"), Span(cust, cls="val"), cls="row"),
                        Div(Span("Stager", cls="label"), Span(stagers, cls="val"), cls="row"),
                        Div(Span("Movers", cls="label"), Span(movers, cls="val"), cls="row"),
                        cls="persons", style="margin-top:10px",
                    ),
                    Div(
                        _sub_page_link("Design", "Staging_Design", staging_id=r["ID"]),
                        _sub_page_link("Pictures", "Staging_Videos_and_Pictures", staging_id=r["ID"]),
                        _sub_page_link("Packing", "Packing_Guide_Page", staging_id=r["ID"]),
                        _sub_page_link("Setup", "Staging_Setup_Guide", staging_id=r["ID"]),
                        cls="sublinks",
                    ),
                    cls=f"card{' today' if is_today else ''}",
                ))
        d += timedelta(days=1)

    return Div(*items, cls="cards")


# -------------------- route --------------------

def _page_head(title):
    return Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1, viewport-fit=cover"),
        Title(title),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        ),
        _style_block(),
        _script_block(),
    )


def _full_page(title, *body_children):
    """Build a complete <html> document, bypassing fast_app's Pico wrapper."""
    doc = Html(
        _page_head(title),
        Body(*body_children),
        lang="en",
    )
    rendered = to_xml(doc)
    if not rendered.lstrip().lower().startswith("<!doctype"):
        rendered = "<!doctype html>\n" + rendered
    return HTMLResponse(rendered)


def register(rt):

    @rt("/staging_task_board")
    def task_board(request: Request,
                   display: str = "",
                   show_period: str = "",
                   show_only_my_tasks: str = "",
                   show_stars: str = "",
                   my_name: str = ""):
        display_mode = (display or "desktop").lower()
        if display_mode not in ("desktop", "mobile"):
            display_mode = "desktop"
        period = show_period.lower() if show_period else "this_week"
        if period not in _PERIOD_RANGES:
            period = "this_week"
        show_my = show_only_my_tasks.lower() in ("yes", "true", "1")
        stars = show_stars.lower() in ("yes", "true", "1")

        rows, from_d, to_d, today = _fetch_stagings(period, show_my, stars, my_name.strip())
        grouped = _group_by_date(rows)

        body_content = (
            _mobile_cards(grouped, from_d, to_d, today)
            if display_mode == "mobile"
            else _desktop_table(grouped, from_d, to_d, today)
        )

        return _full_page(
            "Staging Task Board",
            Div(
                _toolbar(display_mode, period, show_my, len(rows), from_d, to_d, today),
                Div(body_content, cls="scroll-area"),
                _modal(),
                cls="app-shell",
            ),
        )

    @rt("/staging_task_board/set_date", methods=["POST"])
    async def set_date(request: Request):
        form = await request.form()
        sid = (form.get("staging_id") or "").strip()
        field = (form.get("field") or "").strip()
        clear = form.get("clear") == "1"

        if not sid or field not in _DATE_FIELDS:
            return RedirectResponse("/staging_task_board?error=bad_params", status_code=303)

        if field.endswith("_Time"):
            new_value = "" if clear else datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        else:
            new_value = "" if clear else _fmt_mdy(date.today())

        with _conn() as c:
            c.execute(f"UPDATE Staging_Report SET {field} = ? WHERE ID = ?", (new_value, sid))
            c.commit()

        qs = {
            "display": request.query_params.get("display", ""),
            "show_period": request.query_params.get("show_period", ""),
            "show_only_my_tasks": request.query_params.get("show_only_my_tasks", ""),
        }
        qs = {k: v for k, v in qs.items() if v}
        path = "/staging_task_board"
        if qs:
            path += "?" + urlencode(qs)
        return RedirectResponse(path, status_code=303)

    @rt("/stub")
    def stub_page(request: Request):
        params = dict(request.query_params)
        page = params.pop("page", "Unknown")
        items = [
            Li(NotStr(f'<span>{k}</span> = {v}')) for k, v in params.items()
        ] if params else [Li(NotStr('<span>no params</span>'))]
        return _full_page(
            f"Not ported · {page}",
            Div(
                Div(
                    Div("Coming soon", cls="pill"),
                    H1(page),
                    P("This page is linked from the Staging Task Board but hasn't been ported yet.",
                      cls="modal-sub"),
                    Ul(*items, cls="params"),
                    A("← Back to Task Board", href="/staging_task_board", cls="toolbar-btn accent",
                      style="margin-top:20px"),
                    cls="stub-card",
                ),
                cls="stub-wrap",
            ),
        )
