"""
Staging Task Board — FastHTML port of Zoho's Staging_Task_Board page.

Reads from data/zoho_sync.db.Staging_Report (Zoho snapshot; auto-sync is
paused during UI-design phase — see project_sync_intervals_to_restore memory).

Field updates write straight to Staging_Report. No Zoho push; changes stay
local so web/iOS/Android all see each other. When Zoho is deprecated,
zoho_sync.db becomes the primary DB and these writes become authoritative.

Render strategy:
- Server fetches every Active + Inquired staging (~124 rows) plus the
  employee list and emits the full table with data-* attributes on each
  row.
- Client-side JS handles all filtering (date range, search, my-tasks) by
  toggling row visibility. Filter state lives in-memory + localStorage,
  never in the URL.
- Buttons that write to the DB still POST back to the server, same as
  before, so the DB stays authoritative.

Sub-pages that aren't ported yet land on /stub; see as_webapp/UNPORTED_PAGES.md.
"""
from datetime import date, datetime, timedelta
import json
import os
import sqlite3
from urllib.parse import quote_plus, urlencode

from fasthtml.common import (
    A, Body, Button, Dialog, Div, Form, H1, H2, H3, Head, Html, Input,
    Label, Li, Link, Main, Meta, Ol, P, Script, Span, Style, Svg, Table,
    Tbody, Td, Th, Thead, Title, Tr, Ul, NotStr, to_xml,
)
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse


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


def _fmt_mdy(d):
    return d.strftime("%m/%d/%Y")


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


def _iso(d):
    return d.strftime("%Y-%m-%d")


def _fmt_time_short(s):
    """'14:00' -> '2PM'; '09:30' -> '9:30AM'. Preserves input if unparseable."""
    if not s:
        return ""
    s = s.strip()
    for fmt in ("%H:%M", "%I:%M %p", "%H:%M:%S"):
        try:
            t = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    else:
        return s
    h, m = t.hour, t.minute
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d}{ampm}" if m else f"{h12}{ampm}"


def _fetch_all_stagings():
    """Every Active + Inquired staging with a scheduled date, sorted
    chronologically. Filtering happens client-side.
    """
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
        ORDER BY {iso} ASC, CAST(ID AS INTEGER) ASC
    """
    with _conn() as c:
        return c.execute(sql).fetchall()


def _fetch_employees():
    """First-name roster for the 'I am…' selector. Only active employees."""
    with _conn() as c:
        try:
            rows = c.execute(
                "SELECT First_Name, Last_Name FROM Employee_Report "
                "WHERE First_Name IS NOT NULL AND First_Name != '' "
                "ORDER BY First_Name, Last_Name"
            ).fetchall()
            names = []
            seen = set()
            for r in rows:
                fn = (r["First_Name"] or "").strip()
                ln = (r["Last_Name"] or "").strip()
                full = f"{fn} {ln}".strip()
                if full and full not in seen:
                    seen.add(full)
                    names.append(full)
            return names
        except Exception:
            return []


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


def _build_autocomplete_corpus(rows, employees):
    """Unique tokens for the search dropdown. Month names, status values,
    addresses, customer names, stager/mover names. All lowercased.
    """
    corpus = set()
    for name in employees:
        corpus.add(name)
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    corpus.update(months)
    corpus.update(weekdays)
    corpus.update(["Active", "Inquired", "Vacant", "Occupied", "Staging", "Destaging"])

    for r in rows:
        for key in ("Customer_First_Name", "Customer_Last_Name", "Property_Type",
                    "Occupancy_Type", "Staging_Type", "Staging_Status", "MLS"):
            val = (r[key] or "").strip()
            if val and len(val) >= 2:
                corpus.add(val)
        addr = _parse_link(r["Staging_Address"]) or ""
        if addr:
            # Split address into tokens (street name, city) to broaden matches
            for part in addr.replace(",", " ").split():
                if len(part) > 2 and not part[0].isdigit():
                    corpus.add(part.strip(" ,."))
            corpus.add(addr)
        for field in ("Stager", "Staging_Movers", "Destaging_Movers"):
            for name in _parse_people(r[field]):
                if name:
                    corpus.add(name)
    return sorted(corpus, key=lambda s: s.lower())


# -------------------- theme system (unchanged) --------------------

_THEMES = [
    ("default", "Slate", "#4f46e5"),
    ("ocean",   "Ocean", "#0891b2"),
    ("forest",  "Forest", "#059669"),
    ("sunset",  "Sunset", "#ea580c"),
    ("rose",    "Rose",  "#e11d48"),
    ("noir",    "Noir",  "#0a0a0a"),
]


def _style_block():
    return Style("""
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

    :root {
        --bg:#f6f7fb; --surface:#ffffff; --surface-2:#f1f3f9; --surface-3:#e7eaf3;
        --border:#e3e6ef; --border-strong:#c9cfdd;
        --text:#181b2b; --text-muted:#5b6275; --text-faint:#8b91a5;
        --accent:#4f46e5; --accent-hover:#4338ca; --accent-soft:#eef0ff; --accent-fg:#ffffff;
        --success:#059669; --success-soft:#d1fae5;
        --warning:#d97706; --warning-soft:#fef3c7;
        --danger:#dc2626;  --danger-soft:#fee2e2;
        --row-odd:#ffffff; --row-even:#fafbfd; --row-hover:#f4f6fb;
        --row-today:#eff6ff; --row-destage:#fffbeb; --row-inquired:#f3f4f8; --row-inactive:#eeeef2;
        --date-bg: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        --date-text:#78350f; --date-border:#fbbf24;
        --shadow-sm: 0 1px 2px rgba(15,23,42,.06);
        --shadow-md: 0 4px 12px rgba(15,23,42,.08);
        --shadow-lg: 0 12px 32px rgba(15,23,42,.12);
        --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
        --toolbar-h: 64px;
    }
    :root[data-theme="ocean"]  { --accent:#0891b2; --accent-hover:#0e7490; --accent-soft:#ecfeff; }
    :root[data-theme="forest"] { --accent:#059669; --accent-hover:#047857; --accent-soft:#ecfdf5; }
    :root[data-theme="sunset"] { --accent:#ea580c; --accent-hover:#c2410c; --accent-soft:#fff7ed; }
    :root[data-theme="rose"]   { --accent:#e11d48; --accent-hover:#be123c; --accent-soft:#fff1f2; }
    :root[data-theme="noir"]   { --accent:#0a0a0a; --accent-hover:#000000; --accent-soft:#f4f4f5; }

    @media (prefers-color-scheme: dark) {
        :root:not([data-mode="light"]) {
            --bg:#0b0d14; --surface:#141726; --surface-2:#1c2033; --surface-3:#252a42;
            --border:#262a3f; --border-strong:#363b58;
            --text:#e6e8ef; --text-muted:#9ea5bd; --text-faint:#6b7490;
            --accent:#818cf8; --accent-hover:#a5b4fc; --accent-soft:#1e1f3a;
            --success:#34d399; --success-soft:#0f2921;
            --warning:#fbbf24; --warning-soft:#2a2110;
            --danger:#f87171;  --danger-soft:#2a1515;
            --row-odd:#141726; --row-even:#181c2f; --row-hover:#1e2337;
            --row-today:#1a2344; --row-destage:#231a0d; --row-inquired:#171a28; --row-inactive:#111320;
            --date-bg: linear-gradient(135deg, #2a1f0a 0%, #3a2a0d 100%);
            --date-text:#fbbf24; --date-border:#d97706;
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
    :root[data-mode="dark"] {
        --bg:#0b0d14; --surface:#141726; --surface-2:#1c2033; --surface-3:#252a42;
        --border:#262a3f; --border-strong:#363b58;
        --text:#e6e8ef; --text-muted:#9ea5bd; --text-faint:#6b7490;
        --accent:#818cf8; --accent-hover:#a5b4fc; --accent-soft:#1e1f3a;
        --success:#34d399; --success-soft:#0f2921;
        --warning:#fbbf24; --warning-soft:#2a2110;
        --danger:#f87171;  --danger-soft:#2a1515;
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

    /* ---------- layout ---------- */
    .app-shell { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    .toolbar {
        flex: 0 0 var(--toolbar-h);
        display: flex; align-items: center; gap: 12px;
        padding: 0 16px;
        background: var(--surface); border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow-sm); z-index: 20;
    }
    .toolbar-title { font-weight: 700; font-size: 17px; letter-spacing: -0.01em; white-space: nowrap; }
    .toolbar-title .accent { color: var(--accent); }
    .toolbar-spacer { flex: 1; }

    /* unified toolbar button */
    .tbtn {
        all: unset; box-sizing: border-box;
        display: inline-flex; align-items: center; gap: 7px;
        padding: 7px 12px; font-size: 13px; font-weight: 500;
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        cursor: pointer; transition: all 140ms ease;
        font-family: inherit; white-space: nowrap;
    }
    .tbtn:hover { background: var(--surface-2); border-color: var(--border-strong); }
    .tbtn.on { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
    .tbtn.needs-setup { border-style: dashed; color: var(--text-faint); }
    .tbtn.needs-setup:hover { color: var(--text); }
    .tbtn.accent { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
    .tbtn.accent:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .tbtn svg { width: 15px; height: 15px; flex-shrink: 0; }

    .range-btn { min-width: 200px; justify-content: center; }
    .range-btn .range-count { font-weight: 600; color: var(--accent); }
    .range-btn .range-dash { color: var(--text-faint); margin: 0 4px; }

    /* search */
    .search-wrap { position: relative; flex: 1 1 420px; max-width: 520px; min-width: 200px; }
    .search-input {
        width: 100%; padding: 9px 14px 9px 36px;
        background: var(--surface-2); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        font-family: inherit; font-size: 13px;
        transition: all 140ms ease;
    }
    .search-input:focus { outline: none; border-color: var(--accent); background: var(--surface); box-shadow: 0 0 0 3px var(--accent-soft); }
    .search-icon {
        position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
        color: var(--text-faint); pointer-events: none;
    }
    .search-suggest {
        position: absolute; top: calc(100% + 4px); left: 0; right: 0;
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md); box-shadow: var(--shadow-md);
        max-height: 280px; overflow-y: auto; z-index: 30;
        padding: 4px; display: none;
    }
    .search-suggest.open { display: block; }
    .search-suggest .item {
        padding: 8px 12px; cursor: pointer; border-radius: var(--radius-sm);
        font-size: 13px; color: var(--text);
    }
    .search-suggest .item:hover, .search-suggest .item.hl { background: var(--accent-soft); color: var(--accent); }
    .search-suggest .hint { padding: 4px 12px; font-size: 11px; color: var(--text-faint); border-top: 1px solid var(--border); margin-top: 4px; }
    .search-suggest .hint kbd { background: var(--surface-2); border: 1px solid var(--border); border-radius: 3px; padding: 1px 4px; font-size: 10px; font-family: inherit; }

    /* scroll area */
    .scroll-area { flex: 1; overflow: auto; position: relative; background: var(--bg); }

    /* table */
    table.board { width: 100%; border-collapse: separate; border-spacing: 0; background: var(--surface); font-size: 13px; }
    table.board thead tr { position: sticky; top: 0; z-index: 5; background: var(--surface-2); }
    table.board thead th {
        text-align: left; font-weight: 600; font-size: 12px;
        text-transform: uppercase; letter-spacing: 0.04em;
        color: var(--text-muted); padding: 12px 14px;
        border-bottom: 1px solid var(--border); white-space: nowrap;
    }
    table.board tbody td { padding: 14px; vertical-align: top; border-bottom: 1px solid var(--border); min-width: 240px; max-width: 340px; }
    table.board tbody td.col-wide { min-width: 280px; max-width: 420px; }
    table.board tbody td.col-narrow { min-width: 180px; max-width: 220px; }

    tr.data-row td { background: var(--row-odd); transition: background 120ms ease; }
    tr.data-row:nth-child(even) td { background: var(--row-even); }
    tr.data-row:hover td { background: var(--row-hover); }
    tr.data-row.state-today td { background: var(--row-today); }
    tr.data-row.state-destage td { background: var(--row-destage); }
    tr.data-row.state-inquired td { background: var(--row-inquired); }

    tr.date-banner td {
        background: var(--date-bg); color: var(--date-text);
        font-weight: 700; font-size: 12px;
        text-transform: uppercase; letter-spacing: 0.06em;
        text-align: left; padding: 5px 14px;
        border-top: 1px solid var(--date-border);
        border-bottom: 1px solid var(--date-border);
        position: sticky; top: 41px; z-index: 4;
    }

    tr.empty-state td {
        text-align: center; padding: 40px 20px;
        color: var(--text-muted); font-size: 14px;
    }
    tr.empty-state .emoji { font-size: 32px; display: block; margin-bottom: 8px; opacity: 0.7; }

    /* row cell content */
    .staging-title { font-weight: 700; font-size: 14px; color: var(--text); margin-bottom: 4px; letter-spacing: -0.01em; }
    .staging-meta { color: var(--text-muted); font-size: 12px; margin-bottom: 2px; }
    .staging-items {
        font-size: 12px; color: var(--text-muted); margin-bottom: 4px;
        font-variant-numeric: tabular-nums;
    }
    .staging-address-row {
        display: flex; align-items: center; gap: 6px; flex-wrap: nowrap;
        font-size: 13px; margin-bottom: 2px; min-width: 0;
    }
    .staging-address-row .st-time {
        font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums;
        white-space: nowrap; flex-shrink: 0;
    }
    .staging-address-row .st-addr {
        font-weight: 600; color: var(--text);
        flex: 1 1 auto; min-width: 0;
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .staging-address-row .map-link,
    .staging-address-row .st-drive { flex-shrink: 0; }
    .staging-address-row .st-drive {
        font-size: 11px; color: var(--text-muted);
        padding: 1px 7px; background: var(--surface-2);
        border-radius: 999px; border: 1px solid var(--border);
        font-variant-numeric: tabular-nums;
    }
    .map-link {
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px; border-radius: var(--radius-sm);
        text-decoration: none; color: var(--text-muted);
        transition: all 140ms ease; font-size: 14px; line-height: 1;
    }
    .map-link:hover { background: var(--accent-soft); color: var(--accent); }
    .staging-address { font-weight: 600; color: var(--text); margin-top: 2px; }
    .sublinks { display: flex; flex-wrap: nowrap; gap: 6px; margin-top: 8px; min-width: 0; }
    .sublinks .sublink { flex-shrink: 0; }
    .sublink { font-size: 11px; font-weight: 500; padding: 3px 8px; border-radius: var(--radius-sm); background: var(--accent-soft); color: var(--accent); text-decoration: none; transition: background 140ms ease; }
    .sublink:hover { background: var(--accent); color: var(--accent-fg); }

    .chips { display: flex; flex-wrap: wrap; gap: 6px; }
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

    .money-block { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; font-size: 12px; }
    .money-block .label { color: var(--text-muted); }
    .money-block .val { font-variant-numeric: tabular-nums; font-weight: 500; }
    .money-block .val.owing { color: var(--danger); font-weight: 600; }

    .notes { font-size: 12px; color: var(--text-muted); line-height: 1.5; max-height: 260px; overflow-y: auto; }
    .persons { font-size: 12px; }
    .persons .row { margin-bottom: 4px; }
    .persons .label { color: var(--text-faint); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; margin-right: 4px; }
    .persons .val { color: var(--text); font-weight: 500; }

    /* modals */
    dialog.modal { border: 0; padding: 0; background: transparent; max-width: min(520px, 94vw); width: 100%; }
    dialog#date-modal { max-width: min(760px, 94vw); }
    dialog.modal::backdrop { background: rgba(15,23,42,.5); backdrop-filter: blur(4px); }
    dialog.modal .modal-card { background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); padding: 24px; max-height: 85vh; overflow-y: auto; }
    .modal-title { font-size: 18px; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.01em; }
    .modal-sub { font-size: 13px; color: var(--text-muted); margin: 0 0 20px; }
    .modal-section { margin-top: 20px; }
    .modal-section h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 0 0 10px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 24px; position: sticky; bottom: -24px; background: var(--surface); padding: 16px 0 0; border-top: 1px solid var(--border); margin-bottom: -24px; padding-bottom: 24px; z-index: 2; }

    /* date-range modal */
    .preset-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 4px; }
    .preset-row .tbtn { justify-content: center; padding: 10px; font-size: 13px; }
    .preset-row .tbtn.on { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }

    .cal-wrap { position: relative; margin-top: 14px; }
    .cal-nav {
        all: unset; position: absolute; top: 8px; z-index: 2;
        width: 28px; height: 28px; line-height: 24px; text-align: center;
        font-size: 20px; font-weight: 400; color: var(--text-muted);
        background: var(--surface-2); border: 1px solid var(--border);
        border-radius: 999px; cursor: pointer; transition: all 140ms ease;
    }
    .cal-nav:hover { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
    .cal-nav.prev { left: 8px; }
    .cal-nav.next { right: 8px; }

    .tb-calendar {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
        padding: 4px;
    }
    .cal-month {
        background: var(--surface-2); border: 1px solid var(--border);
        border-radius: var(--radius-md); padding: 10px;
    }
    .cal-month-title {
        text-align: center; font-weight: 700; font-size: 13px;
        color: var(--text); margin: 0 0 6px; letter-spacing: -0.01em;
    }
    .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; }
    .cal-dow {
        text-align: center; padding: 3px 0; font-size: 10px;
        color: var(--text-faint); font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.04em;
    }
    .cal-day {
        all: unset; box-sizing: border-box;
        display: flex; align-items: center; justify-content: center;
        aspect-ratio: 1; min-height: 26px;
        font-size: 12px; color: var(--text);
        border-radius: var(--radius-sm); cursor: pointer;
        transition: all 120ms ease; position: relative;
    }
    .cal-day.empty { visibility: hidden; pointer-events: none; }
    .cal-day:hover { background: var(--accent-soft); }
    .cal-day.today { font-weight: 700; color: var(--accent); }
    .cal-day.today::after {
        content: ''; position: absolute; bottom: 3px; left: 50%;
        transform: translateX(-50%); width: 4px; height: 4px;
        border-radius: 50%; background: var(--accent);
    }
    .cal-day.in-range { background: var(--accent); color: var(--accent-fg); border-radius: 0; }
    .cal-day.range-start { background: var(--accent); color: var(--accent-fg); font-weight: 600; border-radius: var(--radius-sm) 0 0 var(--radius-sm); }
    .cal-day.range-end { background: var(--accent); color: var(--accent-fg); font-weight: 600; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
    .cal-day.range-start.range-end { border-radius: var(--radius-sm); }
    .cal-day.in-range.today::after, .cal-day.range-start.today::after, .cal-day.range-end.today::after { background: var(--accent-fg); }

    .range-summary {
        margin-top: 14px; padding: 10px 14px; font-size: 13px;
        background: var(--surface-2); border: 1px solid var(--border);
        border-radius: var(--radius-md); color: var(--text-muted);
        text-align: center; font-variant-numeric: tabular-nums;
    }
    .range-summary strong { color: var(--text); font-weight: 600; }

    /* settings modal — theme grid */
    .theme-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .theme-card { position: relative; padding: 12px; cursor: pointer; border: 2px solid var(--border); border-radius: var(--radius-md); background: var(--surface); transition: all 140ms ease; text-align: left; font-family: inherit; }
    .theme-card:hover { border-color: var(--border-strong); }
    .theme-card.active { border-color: var(--accent); background: var(--accent-soft); }
    .theme-swatch { display: block; height: 32px; border-radius: var(--radius-sm); margin-bottom: 8px; background: var(--sw, #4f46e5); }
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
    .mode-seg button { padding: 7px 14px; font-size: 13px; font-weight: 500; background: transparent; color: var(--text-muted); border: 0; border-radius: 7px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-family: inherit; }
    .mode-seg button:hover { color: var(--text); }
    .mode-seg button.on { background: var(--surface); color: var(--accent); box-shadow: var(--shadow-sm); }

    .me-select {
        width: 100%; padding: 9px 12px;
        background: var(--surface-2); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        font-family: inherit; font-size: 13px;
    }
    .me-select:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }

    /* stub */
    .stub-wrap { max-width: 560px; margin: 80px auto; padding: 0 20px; }
    .stub-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 32px; box-shadow: var(--shadow-md); }
    .stub-card h1 { margin: 0 0 8px; font-size: 22px; letter-spacing: -0.02em; }
    .stub-card .pill { display: inline-block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--warning); background: var(--warning-soft); padding: 3px 10px; border-radius: 999px; margin-bottom: 14px; }
    .stub-card .params { list-style: none; padding: 12px; margin: 16px 0; background: var(--surface-2); border-radius: var(--radius-md); font-family: 'SF Mono', Menlo, monospace; font-size: 12px; }
    .stub-card .params li { padding: 2px 0; color: var(--text); }
    .stub-card .params li span { color: var(--text-muted); }

    /* scrollbars */
    .scroll-area::-webkit-scrollbar, .modal-card::-webkit-scrollbar, .notes::-webkit-scrollbar, .search-suggest::-webkit-scrollbar { width: 10px; height: 10px; }
    .scroll-area::-webkit-scrollbar-thumb, .modal-card::-webkit-scrollbar-thumb, .notes::-webkit-scrollbar-thumb, .search-suggest::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 5px; border: 2px solid var(--bg); }

    /* ---------- view switcher ---------- */
    .view-seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 3px; gap: 2px; }
    .view-seg button {
        all: unset; box-sizing: border-box; cursor: pointer; font-family: inherit;
        padding: 6px 12px; font-size: 12px; font-weight: 500; color: var(--text-muted);
        border-radius: 7px; display: inline-flex; align-items: center; gap: 5px;
        transition: all 140ms ease;
    }
    .view-seg button:hover { color: var(--text); }
    .view-seg button.on { background: var(--surface); color: var(--accent); box-shadow: var(--shadow-sm); font-weight: 600; }
    .view-seg svg { width: 13px; height: 13px; flex-shrink: 0; }

    /* ---------- view panes ---------- */
    .view-area { flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
    .view-pane { display: none; flex: 1; min-height: 0; overflow: hidden; flex-direction: column; }
    .view-pane.active { display: flex; }
    .view-pane .scroll-area { flex: 1; overflow: auto; background: var(--bg); }

    /* ---------- calendar view ---------- */
    .cal-view-toolbar {
        display: flex; align-items: center; gap: 8px; padding: 10px 16px;
        background: var(--surface); border-bottom: 1px solid var(--border);
        flex-shrink: 0; flex-wrap: wrap;
    }
    .cal-view-toolbar .spacer { flex: 1; }
    .cal-view-title { font-size: 14px; font-weight: 700; letter-spacing: -0.01em; color: var(--text); }
    .cal-view-toolbar .mode-seg button { padding: 6px 12px; font-size: 12px; font-weight: 500; }

    .cal-view-scroll { flex: 1; overflow: auto; padding: 14px 14px 20px; background: var(--bg); }
    .cal-view-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
    .cal-view-dow {
        text-align: center; padding: 4px 0 6px; font-size: 11px;
        font-weight: 600; color: var(--text-faint);
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .cal-view-day {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md); min-height: 130px; padding: 6px;
        display: flex; flex-direction: column; gap: 4px;
        transition: border-color 120ms ease, background 120ms ease;
    }
    .cal-view-day.weekend { background: var(--surface-2); }
    .cal-view-day.today { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-soft); }
    .cal-view-day.drop-over { border-color: var(--accent); background: var(--accent-soft); }

    .cal-view-day-head {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0 2px 2px; font-size: 10px; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;
    }
    .cal-view-day-num { font-size: 13px; font-weight: 700; color: var(--text); }
    .cal-view-day.today .cal-view-day-num,
    .cal-view-day.today .cal-view-day-head { color: var(--accent); }

    .cal-cards-source { display: none; }

    .cal-card {
        display: flex; flex-direction: column; gap: 2px;
        padding: 6px 8px; border-radius: var(--radius-sm);
        background: var(--surface); border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        cursor: grab; font-size: 12px; color: var(--text);
        transition: box-shadow 140ms ease, transform 140ms ease;
    }
    .cal-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
    .cal-card:active { cursor: grabbing; }
    .cal-card.dragging { opacity: 0.4; }
    .cal-card.state-today { border-left-color: var(--accent); background: var(--accent-soft); }
    .cal-card.state-destage { border-left-color: var(--warning); background: var(--warning-soft); }
    .cal-card.state-inquired { border-left-color: var(--text-faint); }

    .cal-card-head {
        display: flex; justify-content: space-between; align-items: center;
        gap: 6px; font-size: 10px; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase; color: var(--text-muted);
    }
    .cal-card.state-destage .cal-card-head { color: var(--warning); }
    .cal-card.state-today .cal-card-head { color: var(--accent); }
    .cal-card-cust {
        color: var(--text); font-weight: 600; font-size: 11px;
        text-transform: none; letter-spacing: 0;
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        max-width: 60%;
    }
    .cal-card-addr {
        font-weight: 600; color: var(--text); font-size: 12px; line-height: 1.3;
        overflow: hidden; text-overflow: ellipsis; display: -webkit-box;
        -webkit-line-clamp: 2; -webkit-box-orient: vertical;
    }
    .cal-card-meta {
        font-size: 10px; color: var(--text-muted); white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
    }

    /* hide date-range button in Calendar view */
    html[data-view="calendar"] #range-btn { display: none; }

    /* ---------- responsive: auto collapse at narrow viewports ---------- */
    @media (max-width: 960px) {
        /* Hide lower-priority columns in desktop table */
        table.board th.col-notes, table.board td.col-notes,
        table.board th.col-moving, table.board td.col-moving,
        table.board th.col-listing, table.board td.col-listing {
            display: none;
        }
    }
    @media (max-width: 720px) {
        .toolbar { flex-wrap: wrap; height: auto; padding: 10px; gap: 8px; }
        :root { --toolbar-h: auto; }
        .toolbar-title { flex: 1 0 100%; }
        .search-wrap { order: 3; flex: 1 1 100%; min-width: 0; }
        .range-btn { min-width: 0; flex: 1; }

        /* Collapse table to stacked cards. Each row becomes a block. */
        table.board, table.board thead, table.board tbody, table.board tr, table.board td { display: block; }
        table.board thead { display: none; }
        table.board tbody tr.data-row { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); margin: 10px; overflow: hidden; }
        table.board tbody tr.data-row td { max-width: none; min-width: 0; border-bottom: 1px solid var(--border); padding: 10px 14px; }
        table.board tbody tr.data-row td:last-child { border-bottom: 0; }
        table.board tbody tr.data-row td::before { content: attr(data-label); display: block; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-faint); margin-bottom: 4px; font-weight: 600; }
        table.board tbody tr.date-banner td { border-radius: var(--radius-md); margin: 10px; position: static; }
        table.board tbody tr.date-banner td::before { display: none; }
        .theme-grid { grid-template-columns: repeat(2, 1fr); }
        .preset-grid { grid-template-columns: repeat(2, 1fr); }
        .tb-calendar { grid-template-columns: 1fr; gap: 12px; }
        .cal-month { padding: 14px; }
        .cal-month-title { font-size: 14px; margin: 0 0 10px; }
        .cal-grid { gap: 2px; }
        .cal-dow { padding: 6px 0; font-size: 11px; }
        .cal-day { min-height: 34px; font-size: 13px; }

        /* Calendar view: stack days vertically on narrow screens */
        .cal-view-grid { grid-template-columns: 1fr; }
        .cal-view-dow { display: none; }
        .cal-view-day { min-height: auto; }
        .cal-view-day-head { border-bottom: 1px solid var(--border); padding-bottom: 4px; margin-bottom: 2px; }
    }
    """)


# -------------------- icons --------------------

def _icon(d, size=15):
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
_ICON_CAL = "M19 4H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z M16 2v4 M8 2v4 M3 10h18"
_ICON_USER = "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"
_ICON_SEARCH = "M21 21l-6-6 M10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14z"


# -------------------- modals --------------------

def _date_modal():
    return Dialog(
        Div(
            H2("Date Range", cls="modal-title"),
            P("Filter stagings by date. Pick a preset or click days on the calendar.",
              cls="modal-sub"),

            Div(
                Button("Today", type="button", cls="tbtn", id="preset-today",
                       onclick="TB.stagePreset('today')"),
                Button("Week", type="button", cls="tbtn", id="preset-week",
                       onclick="TB.stagePreset('week')"),
                Button("All Time", type="button", cls="tbtn", id="preset-all",
                       onclick="TB.stagePreset('all')"),
                cls="preset-row",
            ),

            Div(
                Button(NotStr("‹"), type="button", cls="cal-nav prev",
                       onclick="TB.calMonth(-1)", **{"aria-label": "Previous month"}),
                Div(id="tb-calendar", cls="tb-calendar"),
                Button(NotStr("›"), type="button", cls="cal-nav next",
                       onclick="TB.calMonth(1)", **{"aria-label": "Next month"}),
                cls="cal-wrap",
            ),

            Div(id="tb-range-summary", cls="range-summary"),

            Div(
                Button("Cancel", type="button", cls="tbtn",
                       onclick="TB.closeModal('date-modal')"),
                Button("Apply", type="button", cls="tbtn accent",
                       onclick="TB.applyStagedRange()"),
                cls="modal-actions",
            ),
            cls="modal-card",
        ),
        id="date-modal", cls="modal",
    )


def _settings_modal(employees):
    theme_cards = []
    for slug, name, swatch in _THEMES:
        theme_cards.append(
            Button(
                NotStr('<span class="check">✓</span>'),
                NotStr(f'<span class="theme-swatch" style="--sw:{swatch}"></span>'),
                NotStr(f'<span class="theme-name">{name}</span>'),
                type="button", cls="theme-card",
                **{"data-theme": slug, "onclick": f"TB.setTheme('{slug}')"},
            )
        )

    options_html = '<option value="">— pick your name —</option>'
    for name in employees:
        safe = name.replace('"', "&quot;")
        options_html += f'<option value="{safe}">{safe}</option>'

    return Dialog(
        Div(
            H2("Appearance & identity", cls="modal-title"),
            P("Stored on this device only. 'Who am I' filters the 'My tasks' toggle.", cls="modal-sub"),

            Div(
                H3("Who am I?"),
                NotStr(
                    '<select id="me-select" class="me-select" '
                    'onchange="TB.setMe(this.value)">'
                    + options_html
                    + '</select>'
                ),
                cls="modal-section",
            ),

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
                Button("Done", type="button", cls="tbtn accent", onclick="TB.closeModal('settings-modal')"),
                cls="modal-actions",
            ),
            cls="modal-card",
        ),
        id="settings-modal", cls="modal",
    )


# -------------------- toolbar --------------------

def _toolbar():
    """Toolbar is rendered by the server; live counts + range text are
    updated by JS from the client state."""
    return Div(
        Div(NotStr("Staging "), Span("Task Board", cls="accent"), cls="toolbar-title"),

        Div(
            Button("Table", type="button",
                   **{"data-view": "table", "onclick": "TB.setView('table')"}),
            Button("Calendar", type="button",
                   **{"data-view": "calendar", "onclick": "TB.setView('calendar')"}),
            cls="view-seg", id="view-seg",
        ),

        Button(
            _icon(_ICON_CAL),
            Span(NotStr('<span id="range-count" class="range-count">—</span> stagings '
                        '<span class="range-dash">·</span> '
                        '<span id="range-label">this week</span>')),
            type="button", cls="tbtn range-btn",
            id="range-btn",
            onclick="TB.openDateModal()",
        ),

        Div(
            Span(_icon(_ICON_SEARCH, 16), cls="search-icon"),
            Input(
                type="search", id="tb-search", cls="search-input",
                placeholder="Search address, person, date, notes…",
                autocomplete="off", spellcheck="false",
            ),
            Div(id="search-suggest", cls="search-suggest"),
            cls="search-wrap",
        ),

        Button(
            _icon(_ICON_USER), Span(id="mytasks-label"), NotStr(" My tasks"),
            type="button", cls="tbtn", id="mytasks-btn",
            onclick="TB.toggleMyTasks()",
        ),

        Button(
            _icon(_ICON_PALETTE), Span(" Settings"),
            type="button", cls="tbtn",
            onclick="TB.openModal('settings-modal')",
        ),

        cls="toolbar",
    )


# -------------------- row rendering --------------------

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
    d = _parse_mdy(row["Coming_Staging_Destaging_Date"])
    occ = (row["Occupancy_Type"] or "").strip()
    prop = (row["Property_Type"] or "").strip()
    dd = _parse_mdy(row["Destaging_Date"])
    is_destage = bool(dd and d == dd)

    # Line 1: "Apr 22 Wed  Vacant Condo"  (flag Destage days up front)
    title_bits = []
    if d:
        title_bits.append(d.strftime("%b %-d %a"))
    if is_destage:
        title_bits.append("(Destage)")
    if occ:
        title_bits.append(occ)
    if prop:
        title_bits.append(prop)
    title_line = " ".join(title_bits)

    # Line 2: "— Remaining / 9 in Design".
    # TODO: "Remaining" = items at warehouse that belong to this staging.
    # Needs a staging→items linkage we don't yet have on this page (Item_Report
    # only knows Current_Location). Will wire up when the Design view ships.
    try:
        in_design = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        in_design = 0
    items_line = f"— Remaining / {in_design} in Design"

    # Line 3: "12PM  917-25 Cole St, Toronto  🗺  40mins"
    eta = _fmt_time_short(row["Staging_ETA"] or "")
    drive = (row["Driving_Time"] or "").strip()
    address = _parse_link(row["Staging_Address"]) or row["Staging_Display_Name"] or "—"
    maps_url = (
        "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(address)
        if address and address != "—" else ""
    )

    addr_children = []
    if eta:
        addr_children.append(Span(eta, cls="st-time"))
    addr_children.append(Span(address, cls="st-addr"))
    if maps_url:
        addr_children.append(
            A(NotStr("🗺"), href=maps_url, target="_blank",
              cls="map-link", title="Open directions in Google Maps")
        )
    if drive:
        addr_children.append(Span(f"{drive}mins", cls="st-drive"))

    sid = row["ID"]
    return Td(
        Div(title_line, cls="staging-title"),
        Div(items_line, cls="staging-items"),
        Div(*addr_children, cls="staging-address-row"),
        Div(
            _sub_page_link("Staging", "Staging_Edit", staging_id=sid),
            _sub_page_link("Design", "Staging_Design", staging_id=sid),
            _sub_page_link("Pictures", "Staging_Videos_and_Pictures", staging_id=sid),
            _sub_page_link("Packing", "Packing_Guide_Page", staging_id=sid, staging_type="Staging"),
            _sub_page_link("Setup", "Staging_Setup_Guide", staging_id=sid),
            cls="sublinks",
        ),
        cls="col-wide", **{"data-label": "Staging"},
    )


def _col_persons(row):
    cust = f"{row['Customer_First_Name'] or ''} {row['Customer_Last_Name'] or ''}".strip() or "—"
    stagers = ", ".join(_parse_people(row["Stager"])) or "—"
    movers = ", ".join(_parse_people(row["Staging_Movers"])) or "—"
    destage = ", ".join(_parse_people(row["Destaging_Movers"]))

    rows = [
        Div(Span("Customer", cls="label"), Span(cust, cls="val"), cls="row"),
        Div(Span("Stager", cls="label"), Span(stagers, cls="val"), cls="row"),
        Div(Span("Movers", cls="label"), Span(movers, cls="val"), cls="row"),
    ]
    if destage:
        rows.append(Div(Span("Destage", cls="label"), Span(destage, cls="val"), cls="row"))

    return Td(Div(*rows, cls="persons"), **{"data-label": "Persons"})


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
    return Td(Div(*chips, cls="chips"), **{"data-label": "Tasks"})


def _col_moving(row):
    text = (row["Staging_Moving_Instructions"] or "").strip()
    return Td(
        Div(NotStr(text.replace("\n", "<br>")) if text else Span("—", cls="staging-meta"), cls="notes"),
        cls="col-moving", **{"data-label": "Moving Instructions"},
    )


def _col_notes(row):
    text = (row["General_Notes"] or "").strip()
    return Td(
        Div(NotStr(text.replace("\n", "<br>")) if text else Span("—", cls="staging-meta"), cls="notes"),
        cls="col-notes", **{"data-label": "General Notes"},
    )


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
        **{"data-label": "Accounting"},
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
            _chip_button(sid, "After_Picture_Upload_Date", "After pics up",
                         bool(row["After_Picture_Upload_Date"])),
            cls="chips", style="margin-top:6px",
        )
    )
    if mls:
        children.append(
            Div(Span("MLS  ", cls="label"), Span(mls, cls="val"),
                cls="persons", style="margin-top:8px;font-size:12px")
        )
    if housesigma:
        children.append(A("HouseSigma ↗", href=housesigma, target="_blank",
                          cls="btn", style="margin-top:6px"))
    children.append(
        A("Update MLS info",
          href=f"/stub?{urlencode({'page':'Staging_Edit','staging_id':sid,'focus':'MLS'})}",
          cls="btn", style="margin-top:6px")
    )
    return Td(
        Div(*children, cls="btn-row", style="flex-direction:column;align-items:flex-start"),
        cls="col-narrow col-listing", **{"data-label": "Listing"},
    )


def _row_state(row, coming):
    today = date.today()
    status = (row["Staging_Status"] or "").lower()
    dd = _parse_mdy(row["Destaging_Date"])

    if status == "inquired":
        return "state-inquired"
    if dd and coming == dd:
        return "state-destage"
    if coming == today:
        return "state-today"
    return ""


def _build_row(row, serial):
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])
    coming_iso = coming.isoformat() if coming else ""

    # searchable blob: address, customer, people, notes, status, etc.
    bits = [
        row["Staging_Display_Name"] or "",
        _parse_link(row["Staging_Address"]) or "",
        f"{row['Customer_First_Name'] or ''} {row['Customer_Last_Name'] or ''}",
        row["Customer_Phone"] or "",
        row["Customer_Email"] or "",
        row["Occupancy_Type"] or "",
        row["Property_Type"] or "",
        row["Staging_Type"] or "",
        row["Staging_Status"] or "",
        row["MLS"] or "",
        row["General_Notes"] or "",
        row["Staging_Moving_Instructions"] or "",
        row["Destaging_Moving_Instructions"] or "",
        _fmt_mdy(coming) if coming else "",
    ]
    people = []
    for f in ("Stager", "Staging_Movers", "Destaging_Movers"):
        people.extend(_parse_people(row[f]))
    bits.extend(people)
    if coming:
        bits.append(coming.strftime("%B"))
        bits.append(coming.strftime("%A"))
    searchable = " ".join(x for x in bits if x).lower()

    return Tr(
        _col_staging(row, serial),
        _col_persons(row),
        _col_actions(row),
        _col_moving(row),
        _col_notes(row),
        _col_accounting(row),
        _col_listing(row),
        cls=f"data-row {_row_state(row, coming)}",
        **{
            "data-record": "table",
            "data-date": coming_iso,
            "data-people": "|".join(p.lower() for p in people),
            "data-search": searchable,
        },
    )


def _build_table(grouped):
    headers = Thead(Tr(
        Th("Staging"), Th("Persons"), Th("Tasks"),
        Th("Moving Instructions", cls="col-moving"),
        Th("General Notes", cls="col-notes"),
        Th("Accounting"),
        Th("Listing", cls="col-listing"),
    ))

    body = []
    for date_str, group in grouped:
        d = _parse_mdy(date_str)
        d_iso = d.isoformat() if d else ""
        banner_text = d.strftime("%A · %B %-d, %Y") if d else date_str
        if d == date.today():
            banner_text += "  (today)"
        body.append(Tr(
            Td(banner_text, colspan="7"),
            cls="date-banner", **{"data-date": d_iso},
        ))
        for i, r in enumerate(group, start=1):
            body.append(_build_row(r, i))

    # Empty-state row — shown by JS when all data rows are hidden
    body.append(Tr(
        Td(
            Span("🔍", cls="emoji"),
            Div("No stagings match your filters."),
            Div("Try a wider date range, clear the search, or toggle My Tasks off.",
                style="font-size:12px;margin-top:4px;color:var(--text-faint)"),
            colspan="7",
        ),
        cls="empty-state",
        id="empty-state",
        style="display:none",
    ))

    return Table(headers, Tbody(*body), cls="board")


# -------------------- shared record data --------------------

def _record_data(row):
    """Shared data-* attrs used by all three views. Keeps filters consistent."""
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])
    coming_iso = coming.isoformat() if coming else ""
    people = []
    for f in ("Stager", "Staging_Movers", "Destaging_Movers"):
        people.extend(_parse_people(row[f]))
    bits = [
        _parse_link(row["Staging_Address"]) or "",
        row["Staging_Display_Name"] or "",
        f"{row['Customer_First_Name'] or ''} {row['Customer_Last_Name'] or ''}",
        row["Customer_Phone"] or "",
        row["Customer_Email"] or "",
        row["Occupancy_Type"] or "",
        row["Property_Type"] or "",
        row["Staging_Type"] or "",
        row["Staging_Status"] or "",
        row["MLS"] or "",
        row["General_Notes"] or "",
        _fmt_mdy(coming) if coming else "",
    ]
    bits.extend(people)
    if coming:
        bits.append(coming.strftime("%B"))
        bits.append(coming.strftime("%A"))
    return {
        "date_iso": coming_iso,
        "people_blob": "|".join(p.lower() for p in people),
        "search_blob": " ".join(x for x in bits if x).lower(),
    }


# -------------------- calendar view --------------------

def _build_calendar_card(row):
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])
    sid = row["ID"]
    addr = _parse_link(row["Staging_Address"]) or row["Staging_Display_Name"] or "—"
    cust_last = (row["Customer_Last_Name"] or "").strip()
    dd = _parse_mdy(row["Destaging_Date"])
    kind = "Destage" if (dd and coming == dd) else "Staging"
    stagers = _parse_people(row["Stager"])
    stager_short = stagers[0].split()[0] if stagers else ""
    try:
        items = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        items = 0

    meta_bits = []
    if stager_short:
        meta_bits.append(stager_short)
    meta_bits.append(f"{items} item{'s' if items != 1 else ''}")

    rec = _record_data(row)

    return Div(
        Div(
            Span(kind),
            Span(cust_last or "—", cls="cal-card-cust"),
            cls="cal-card-head",
        ),
        Div(addr, cls="cal-card-addr"),
        Div(" · ".join(meta_bits), cls="cal-card-meta"),
        cls=f"cal-card {_row_state(row, coming)}",
        draggable="true",
        **{
            "data-record": "cal",
            "data-sid": str(sid),
            "data-date": rec["date_iso"],
            "data-people": rec["people_blob"],
            "data-search": rec["search_blob"],
        },
    )


def _build_calendar_view(rows):
    cards = [_build_calendar_card(r) for r in rows if r["Coming_Staging_Destaging_Date"]]
    toolbar = Div(
        Button("Today", type="button", cls="tbtn", onclick="TB.calViewToday()"),
        Button(NotStr("‹"), type="button", cls="tbtn",
               onclick="TB.calViewShift(-1)", **{"aria-label": "Previous week"}),
        Button(NotStr("›"), type="button", cls="tbtn",
               onclick="TB.calViewShift(1)", **{"aria-label": "Next week"}),
        Div(id="cal-view-title", cls="cal-view-title", style="margin-left:6px"),
        Div(cls="spacer"),
        Div(
            Button("Week", type="button", id="cal-mode-week",
                   onclick="TB.calViewMode('week')"),
            Button("Month", type="button", id="cal-mode-month",
                   onclick="TB.calViewMode('month')"),
            cls="mode-seg",
        ),
        cls="cal-view-toolbar",
    )
    scroll = Div(
        Div(id="cal-view-grid", cls="cal-view-grid"),
        cls="cal-view-scroll",
    )
    source = Div(*cards, id="cal-cards-source", cls="cal-cards-source")
    return toolbar, scroll, source


# -------------------- client JS --------------------

def _client_script(employees, corpus):
    # Use JSON embedding so Python string escaping doesn't bite us.
    employees_json = json.dumps(employees)
    corpus_json = json.dumps(corpus[:400])  # cap for sanity

    return Script(
        # Embed data as JSON strings the JS reads at startup.
        f"window.TB_EMPLOYEES = {employees_json};\n"
        f"window.TB_CORPUS = {corpus_json};\n"
        # Main controller — uses template literals so keep regex-free and
        # rely on dict-style keys sparingly.
        r"""
(function() {
    const doc = document.documentElement;
    const K = { THEME:'tb_theme', MODE:'tb_mode', ME:'tb_me', RANGE:'tb_range', MY:'tb_mytasks', VIEW:'tb_view', CAL_MODE:'tb_cal_mode' };

    // ---------- state ----------
    const today = new Date(); today.setHours(0,0,0,0);
    const iso = d => d.toISOString().slice(0,10);
    const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate()+n); return x; };
    const fmt = d => d.toLocaleDateString('en-US', {month:'short', day:'numeric'});
    const parseIso = s => { if(!s) return null; const [y,m,d] = s.split('-').map(Number); return new Date(y, m-1, d); };

    const PRESETS = {
        today:    () => ({ from: iso(today), to: iso(today), label: 'today' }),
        week:     () => ({ from: iso(addDays(today,-5)), to: iso(addDays(today,13)), label: 'this week' }),
        all:      () => ({ from: '1970-01-01', to: '2100-12-31', label: 'all time' }),
    };

    // Migrate the old 'original' view key → 'table' (view was renamed).
    const storedView = localStorage.getItem(K.VIEW);
    const initialView = (storedView === 'calendar') ? 'calendar' : 'table';

    const state = {
        range: JSON.parse(localStorage.getItem(K.RANGE) || 'null') || PRESETS.week(),
        search: '',
        mytasks: localStorage.getItem(K.MY) === '1',
        me: localStorage.getItem(K.ME) || '',
        view: initialView,
    };

    // Calendar view state. Anchor is the Sunday at the top of the visible window.
    function sundayOf(d) {
        const x = new Date(d);
        x.setDate(x.getDate() - x.getDay());
        x.setHours(0, 0, 0, 0);
        return x;
    }
    const cal = {
        mode: localStorage.getItem(K.CAL_MODE) || 'week',
        anchor: sundayOf(today),
    };

    // ---------- theme / mode ----------
    function applyChrome() {
        const theme = localStorage.getItem(K.THEME) || 'default';
        const mode = localStorage.getItem(K.MODE) || 'auto';
        if (theme === 'default') doc.removeAttribute('data-theme');
        else doc.setAttribute('data-theme', theme);
        if (mode === 'auto') doc.removeAttribute('data-mode');
        else doc.setAttribute('data-mode', mode);
    }
    applyChrome();

    // ---------- filtering ----------
    function matches(el) {
        // Calendar cells already bound the date window, so skip range filter there.
        const isCal = el.dataset.record === 'cal';
        if (!isCal) {
            const d = el.dataset.date;
            if (d < state.range.from || d > state.range.to) return false;
        }
        if (state.mytasks && state.me) {
            const people = el.dataset.people || '';
            if (!people.includes(state.me.toLowerCase())) return false;
        }
        if (state.search) {
            const s = el.dataset.search || '';
            const tokens = state.search.toLowerCase().split(/\s+/).filter(Boolean);
            for (const t of tokens) { if (!s.includes(t)) return false; }
        }
        return true;
    }

    function hideEmptyGroupHeaders(headerSel, rowCls) {
        document.querySelectorAll(headerSel).forEach(b => {
            let next = b.nextElementSibling;
            let anyVisible = false;
            while (next && !next.matches(headerSel)) {
                if (next.classList.contains(rowCls) && next.style.display !== 'none') { anyVisible = true; break; }
                next = next.nextElementSibling;
            }
            b.style.display = anyVisible ? '' : 'none';
        });
    }

    function applyFilters() {
        let countTable = 0;
        document.querySelectorAll('[data-record]').forEach(el => {
            const ok = matches(el);
            el.style.display = ok ? '' : 'none';
            if (ok && el.dataset.record === 'table') countTable++;
        });
        hideEmptyGroupHeaders('tr.date-banner', 'data-row');
        const empty = document.getElementById('empty-state');
        if (empty) empty.style.display = countTable === 0 ? '' : 'none';
        updateRangeLabel(countTable);
        updateMyTasksBtn();
    }

    function updateRangeLabel(count) {
        document.getElementById('range-count').textContent = count;
        const label = state.range.label || (fmt(parseIso(state.range.from)) + ' → ' + fmt(parseIso(state.range.to)));
        document.getElementById('range-label').textContent = label;
    }

    function updateMyTasksBtn() {
        const btn = document.getElementById('mytasks-btn');
        btn.classList.toggle('on', state.mytasks && !!state.me);
        btn.classList.toggle('needs-setup', !state.me);
        btn.title = state.me ? '' : 'Pick your name in Settings → Who am I?';
        const lbl = document.getElementById('mytasks-label');
        if (state.mytasks && state.me) {
            lbl.textContent = ' ' + state.me.split(' ')[0] + ' ·';
        } else {
            lbl.textContent = '';
        }
    }

    // ---------- date range controls (staged until Apply) ----------
    // Staged range only lives while the modal is open. Applied to state.range
    // on "Apply", discarded on "Cancel" / close.
    let staged = { from: state.range.from, to: state.range.to, label: state.range.label };
    let anchorMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    // Flip-flops between 'ready' (next click = new start) and 'pending'
    // (next click = end of the range). Preset clicks and modal-open reset
    // it to 'ready', so the next day-click starts fresh.
    let clickState = 'ready';

    function openDateModal() {
        staged = { from: state.range.from, to: state.range.to, label: state.range.label };
        const a = parseIso(staged.from) || today;
        anchorMonth = new Date(a.getFullYear(), a.getMonth(), 1);
        clickState = 'ready';
        renderCalendar();
        refreshPresetButtons();
        openModal('date-modal');
    }

    function stagePreset(p) {
        const r = PRESETS[p]();
        staged = { from: r.from, to: r.to, label: r.label };
        const a = (p === 'all') ? today : parseIso(staged.from);
        anchorMonth = new Date(a.getFullYear(), a.getMonth(), 1);
        clickState = 'ready';
        renderCalendar();
        refreshPresetButtons();
    }

    function refreshPresetButtons() {
        ['today','week','all'].forEach(p => {
            const r = PRESETS[p]();
            const btn = document.getElementById('preset-' + p);
            if (btn) btn.classList.toggle('on', r.from === staged.from && r.to === staged.to);
        });
    }

    function calMonth(delta) {
        anchorMonth = new Date(anchorMonth.getFullYear(), anchorMonth.getMonth() + delta, 1);
        renderCalendar();
    }

    function renderCalendar() {
        const host = document.getElementById('tb-calendar');
        host.innerHTML = '';
        // Render 2 months: anchorMonth and anchorMonth+1
        for (let off = 0; off < 2; off++) {
            const m = new Date(anchorMonth.getFullYear(), anchorMonth.getMonth() + off, 1);
            host.appendChild(buildMonth(m));
        }
        updateRangeSummary();
    }

    const DOW = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    function buildMonth(firstDay) {
        const month = firstDay.getMonth();
        const year = firstDay.getFullYear();
        const wrap = document.createElement('div');
        wrap.className = 'cal-month';
        const title = document.createElement('div');
        title.className = 'cal-month-title';
        title.textContent = MONTHS[month] + ' ' + year;
        wrap.appendChild(title);
        const grid = document.createElement('div');
        grid.className = 'cal-grid';
        DOW.forEach(d => {
            const h = document.createElement('div');
            h.className = 'cal-dow';
            h.textContent = d;
            grid.appendChild(h);
        });
        // leading empty cells to align weekday
        const leading = firstDay.getDay(); // 0=Sun
        for (let i = 0; i < leading; i++) {
            const c = document.createElement('div');
            c.className = 'cal-day empty';
            grid.appendChild(c);
        }
        // days
        const fromD = parseIso(staged.from);
        const toD = parseIso(staged.to);
        const todayIso = iso(today);
        for (let day = 1; ; day++) {
            const d = new Date(year, month, day);
            if (d.getMonth() !== month) break;
            const cell = document.createElement('button');
            cell.type = 'button';
            cell.className = 'cal-day';
            cell.textContent = String(day);
            const cellIso = iso(d);
            if (cellIso === todayIso) cell.classList.add('today');
            if (fromD && toD) {
                const a = fromD <= toD ? fromD : toD;
                const b = fromD <= toD ? toD : fromD;
                if (d >= a && d <= b) cell.classList.add('in-range');
                if (cellIso === iso(a)) cell.classList.add('range-start');
                if (cellIso === iso(b)) cell.classList.add('range-end');
            }
            cell.addEventListener('click', () => onDayClick(cellIso));
            grid.appendChild(cell);
        }
        wrap.appendChild(grid);
        return wrap;
    }

    function onDayClick(dIso) {
        if (clickState === 'ready') {
            // Start a new range. Show a single-day selection until next click.
            staged = { from: dIso, to: dIso, label: '' };
            clickState = 'pending';
        } else {
            // Complete the range. Swap endpoints if second click is earlier.
            if (dIso < staged.from) {
                staged = { from: dIso, to: staged.from, label: '' };
            } else {
                staged = { from: staged.from, to: dIso, label: '' };
            }
            clickState = 'ready';
        }
        renderCalendar();
        refreshPresetButtons();
    }

    function updateRangeSummary() {
        const el = document.getElementById('tb-range-summary');
        if (!el) return;
        const a = parseIso(staged.from);
        const b = parseIso(staged.to);
        if (!a || !b) { el.innerHTML = '<span>No range selected</span>'; return; }
        if (staged.label && staged.label !== '') {
            el.innerHTML = '<strong>' + staged.label + '</strong> · ' + fmt(a) + ' → ' + fmt(b);
        } else if (iso(a) === iso(b)) {
            el.innerHTML = '<strong>' + a.toLocaleDateString('en-US', {weekday:'long', month:'long', day:'numeric'}) + '</strong>';
        } else {
            const days = Math.round((b - a) / 86400000) + 1;
            el.innerHTML = '<strong>' + fmt(a) + ' → ' + fmt(b) + '</strong> · ' + days + ' days';
        }
    }

    function applyStagedRange() {
        if (!staged.from || !staged.to) return;
        const a = staged.from <= staged.to ? staged.from : staged.to;
        const b = staged.from <= staged.to ? staged.to : staged.from;
        state.range = {
            from: a, to: b,
            label: staged.label || (fmt(parseIso(a)) + ' → ' + fmt(parseIso(b))),
        };
        localStorage.setItem(K.RANGE, JSON.stringify(state.range));
        applyFilters();
        closeModal('date-modal');
    }

    // ---------- search + autocomplete ----------
    const suggest = () => document.getElementById('search-suggest');
    let hlIdx = 0;

    function showSuggestions(q) {
        const el = suggest();
        if (q.length < 2) { el.classList.remove('open'); return; }
        const lo = q.toLowerCase();
        const matches = (window.TB_CORPUS || []).filter(s => s.toLowerCase().includes(lo)).slice(0, 8);
        if (!matches.length) { el.classList.remove('open'); return; }
        el.innerHTML = '';
        matches.forEach((m, i) => {
            const d = document.createElement('div');
            d.className = 'item' + (i === 0 ? ' hl' : '');
            d.textContent = m;
            d.dataset.idx = i;
            d.addEventListener('mousedown', e => { e.preventDefault(); completeWith(m); });
            el.appendChild(d);
        });
        const hint = document.createElement('div');
        hint.className = 'hint';
        hint.innerHTML = '<kbd>Tab</kbd> autocomplete · <kbd>Enter</kbd> search · <kbd>↑↓</kbd> navigate';
        el.appendChild(hint);
        el.classList.add('open');
        hlIdx = 0;
    }

    function moveHl(delta) {
        const items = suggest().querySelectorAll('.item');
        if (!items.length) return;
        items[hlIdx]?.classList.remove('hl');
        hlIdx = (hlIdx + delta + items.length) % items.length;
        items[hlIdx]?.classList.add('hl');
    }

    function highlighted() {
        return suggest().querySelector('.item.hl')?.textContent || '';
    }

    function completeWith(term) {
        const inp = document.getElementById('tb-search');
        inp.value = term;
        state.search = term;
        suggest().classList.remove('open');
        applyFilters();
        inp.focus();
    }

    // ---------- my tasks ----------
    function toggleMyTasks() {
        if (!state.me) {
            // force open settings so user can pick a name
            openModal('settings-modal');
            return;
        }
        state.mytasks = !state.mytasks;
        localStorage.setItem(K.MY, state.mytasks ? '1' : '0');
        applyFilters();
    }

    function setMe(v) {
        state.me = v;
        localStorage.setItem(K.ME, v);
        updateMyTasksBtn();
        applyFilters();
    }

    // ---------- modals ----------
    function openModal(id) {
        refreshModalState();
        const dlg = document.getElementById(id);
        if (dlg && dlg.showModal) dlg.showModal();
    }
    function closeModal(id) {
        const dlg = document.getElementById(id);
        if (dlg && dlg.close) dlg.close();
    }
    document.addEventListener('click', e => {
        // backdrop click closes any open dialog
        document.querySelectorAll('dialog.modal').forEach(dlg => {
            if (dlg.open && e.target === dlg) dlg.close();
        });
    });

    function refreshModalState() {
        // theme cards
        const theme = localStorage.getItem(K.THEME) || 'default';
        document.querySelectorAll('.theme-card').forEach(el => el.classList.toggle('active', el.dataset.theme === theme));
        // mode segments
        const mode = localStorage.getItem(K.MODE) || 'auto';
        document.querySelectorAll('.mode-seg button').forEach(el => el.classList.toggle('on', el.dataset.mode === mode));
        // me select
        const sel = document.getElementById('me-select');
        if (sel) sel.value = state.me;
    }

    // ---------- view switching ----------
    function setView(v) {
        state.view = v;
        localStorage.setItem(K.VIEW, v);
        doc.setAttribute('data-view', v);
        document.querySelectorAll('.view-pane').forEach(p => {
            p.classList.toggle('active', p.dataset.view === v);
        });
        document.querySelectorAll('#view-seg button').forEach(b => {
            b.classList.toggle('on', b.dataset.view === v);
        });
        if (v === 'calendar') renderCalendarGrid();
        applyFilters();
    }

    // ---------- calendar view: grid render ----------
    function renderCalendarGrid() {
        const grid = document.getElementById('cal-view-grid');
        const src = document.getElementById('cal-cards-source');
        if (!grid || !src) return;

        // Move live cards back to source so we can rebuild the grid from scratch.
        grid.querySelectorAll('.cal-card').forEach(c => src.appendChild(c));
        grid.innerHTML = '';

        // Weekday header row (7 cells).
        DOW.forEach(d => {
            const h = document.createElement('div');
            h.className = 'cal-view-dow';
            h.textContent = d;
            grid.appendChild(h);
        });

        const weeks = cal.mode === 'week' ? 2 : 4;
        const totalDays = weeks * 7;
        const cellByIso = new Map();
        const todayIso = iso(today);

        for (let i = 0; i < totalDays; i++) {
            const d = new Date(cal.anchor);
            d.setDate(cal.anchor.getDate() + i);
            const cellIso = iso(d);
            const cell = document.createElement('div');
            cell.className = 'cal-view-day';
            cell.dataset.date = cellIso;
            const dow = d.getDay();
            if (dow === 0 || dow === 6) cell.classList.add('weekend');
            if (cellIso === todayIso) cell.classList.add('today');

            const head = document.createElement('div');
            head.className = 'cal-view-day-head';
            const mlabel = document.createElement('span');
            mlabel.textContent = MONTHS[d.getMonth()].slice(0, 3);
            const num = document.createElement('span');
            num.className = 'cal-view-day-num';
            num.textContent = String(d.getDate());
            head.appendChild(mlabel);
            head.appendChild(num);
            cell.appendChild(head);

            wireCellDrop(cell);
            grid.appendChild(cell);
            cellByIso.set(cellIso, cell);
        }

        // Place cards into cells by data-date. Cards with dates outside
        // the window stay in the hidden source div.
        Array.from(src.querySelectorAll('.cal-card')).forEach(card => {
            const d = card.dataset.date;
            const cell = cellByIso.get(d);
            if (cell) {
                cell.appendChild(card);
                wireCardDrag(card);
            }
        });

        // Title: "Apr 19 – May 2, 2026"
        const first = cal.anchor;
        const last = new Date(cal.anchor);
        last.setDate(last.getDate() + totalDays - 1);
        const title = document.getElementById('cal-view-title');
        if (title) title.textContent = fmt(first) + ' – ' + fmt(last) + ', ' + last.getFullYear();

        // Reflect mode in the seg buttons.
        const mw = document.getElementById('cal-mode-week');
        const mm = document.getElementById('cal-mode-month');
        if (mw) mw.classList.toggle('on', cal.mode === 'week');
        if (mm) mm.classList.toggle('on', cal.mode === 'month');

        applyFilters();
    }

    // ---------- calendar: drag-drop (local only, no DB) ----------
    let draggedCard = null;
    function wireCardDrag(card) {
        if (card._dragWired) return;
        card._dragWired = true;
        card.addEventListener('dragstart', e => {
            draggedCard = card;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            try { e.dataTransfer.setData('text/plain', card.dataset.sid || ''); } catch(_) {}
        });
        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
            draggedCard = null;
        });
    }
    function wireCellDrop(cell) {
        cell.addEventListener('dragover', e => {
            if (!draggedCard) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            cell.classList.add('drop-over');
        });
        cell.addEventListener('dragleave', () => cell.classList.remove('drop-over'));
        cell.addEventListener('drop', e => {
            e.preventDefault();
            cell.classList.remove('drop-over');
            if (!draggedCard) return;
            const newDate = cell.dataset.date;
            if (draggedCard.dataset.date !== newDate) {
                draggedCard.dataset.date = newDate;
                cell.appendChild(draggedCard);
            }
        });
    }

    // ---------- calendar: navigation ----------
    function calViewShift(delta) {
        // Shift one week at a time (feels natural in both modes).
        const d = new Date(cal.anchor);
        d.setDate(d.getDate() + delta * 7);
        cal.anchor = d;
        renderCalendarGrid();
    }
    function calViewToday() {
        cal.anchor = sundayOf(today);
        renderCalendarGrid();
    }
    function calViewMode(m) {
        cal.mode = m;
        localStorage.setItem(K.CAL_MODE, m);
        cal.anchor = sundayOf(today);
        renderCalendarGrid();
    }

    // ---------- wiring ----------
    window.TB = {
        setTheme(t){ localStorage.setItem(K.THEME,t); applyChrome(); refreshModalState(); },
        setMode(m){ localStorage.setItem(K.MODE,m); applyChrome(); refreshModalState(); },
        setMe,
        openDateModal,
        stagePreset,
        calMonth,
        applyStagedRange,
        toggleMyTasks,
        openModal,
        closeModal,
        setView,
        calViewToday,
        calViewShift,
        calViewMode,
    };

    document.addEventListener('DOMContentLoaded', () => {
        const inp = document.getElementById('tb-search');
        inp.addEventListener('input', e => {
            showSuggestions(e.target.value);
            // live-filter as user types
            state.search = e.target.value;
            applyFilters();
        });
        inp.addEventListener('keydown', e => {
            const el = suggest();
            const open = el.classList.contains('open');
            if (e.key === 'ArrowDown' && open) { e.preventDefault(); moveHl(1); }
            else if (e.key === 'ArrowUp' && open) { e.preventDefault(); moveHl(-1); }
            else if (e.key === 'Tab' && open) { e.preventDefault(); completeWith(highlighted() || inp.value); }
            else if (e.key === 'Enter') {
                e.preventDefault();
                if (open && highlighted()) completeWith(highlighted());
                else { state.search = inp.value; applyFilters(); el.classList.remove('open'); }
            }
            else if (e.key === 'Escape') { el.classList.remove('open'); }
        });
        inp.addEventListener('blur', () => { setTimeout(() => suggest().classList.remove('open'), 150); });

        // populate me-select if employees list is available
        // (already populated server-side)
        const sel = document.getElementById('me-select');
        if (sel) sel.value = state.me;

        setView(state.view);
    });
})();
"""
    )


# -------------------- page assembly --------------------

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
    )


def _full_page(title, body_children, extra_scripts=()):
    doc = Html(
        _page_head(title),
        Body(*body_children, *extra_scripts),
        lang="en",
    )
    rendered = to_xml(doc)
    if not rendered.lstrip().lower().startswith("<!doctype"):
        rendered = "<!doctype html>\n" + rendered
    return HTMLResponse(rendered)


# -------------------- routes --------------------

def register(rt):

    @rt("/staging_task_board")
    def task_board(request: Request):
        rows = _fetch_all_stagings()
        employees = _fetch_employees()
        corpus = _build_autocomplete_corpus(rows, employees)
        grouped = _group_by_date(rows)

        table_view = _build_table(grouped)
        cal_toolbar, cal_scroll, cal_source = _build_calendar_view(rows)

        return _full_page(
            "Staging Task Board",
            [Div(
                _toolbar(),
                Div(
                    Div(
                        Div(table_view, cls="scroll-area"),
                        id="view-table", cls="view-pane",
                        **{"data-view": "table"},
                    ),
                    Div(
                        cal_toolbar, cal_scroll, cal_source,
                        id="view-calendar", cls="view-pane",
                        **{"data-view": "calendar"},
                    ),
                    cls="view-area",
                ),
                _date_modal(),
                _settings_modal(employees),
                cls="app-shell",
            )],
            extra_scripts=[_client_script(employees, corpus)],
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

        return RedirectResponse("/staging_task_board", status_code=303)

    @rt("/stub")
    def stub_page(request: Request):
        params = dict(request.query_params)
        page = params.pop("page", "Unknown")
        items = [Li(NotStr(f'<span>{k}</span> = {v}')) for k, v in params.items()] \
                if params else [Li(NotStr('<span>no params</span>'))]
        return _full_page(
            f"Not ported · {page}",
            [Div(
                Div(
                    Div("Coming soon", cls="pill"),
                    H1(page),
                    P("This page is linked from the Staging Task Board but hasn't been ported yet.",
                      cls="modal-sub"),
                    Ul(*items, cls="params"),
                    A("← Back to Task Board", href="/staging_task_board",
                      cls="tbtn accent", style="margin-top:20px"),
                    cls="stub-card",
                ),
                cls="stub-wrap",
            )],
        )
