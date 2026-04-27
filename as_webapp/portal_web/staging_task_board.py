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
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse


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


# Schedulable roster — 3 stagers + 8 movers. Sales (Aashika, Clara) use the
# board to assign work but aren't themselves assigned, so they're omitted.
# Hardcoded so a roster shuffle is one git commit, not a Duty-field hunt.
_STAFF_ROSTER = [
    {"name": "Mona",       "roles": ["stager"]},  # Mrunal
    {"name": "Nency",      "roles": ["stager"]},
    {"name": "Gurleen",    "roles": ["stager"]},
    {"name": "Abhijeet",   "roles": ["mover"]},
    {"name": "Navdeep",    "roles": ["mover"]},
    {"name": "Philpas",    "roles": ["mover"]},
    {"name": "Jashandeep", "roles": ["mover"]},
    {"name": "Jatin",      "roles": ["mover"]},
    {"name": "Ravi",       "roles": ["mover"]},
    {"name": "Ravinder",   "roles": ["mover"]},
    {"name": "Saddam",     "roles": ["mover"]},
]


# Display name → Zoho first_name. Mona is the colloquial name; Zoho stores
# her record under "Mrunal", so reads need to alias forward and writes
# need to alias back.
_NAME_TO_ZOHO = {"Mona": "Mrunal"}
_ZOHO_TO_NAME = {v: k for k, v in _NAME_TO_ZOHO.items()}

# Display name → Zoho ID, used when persisting an assignment back to the
# Stager / Movers JSON columns so the row matches what Zoho would write.
_NAME_TO_ZOHO_ID = {
    "Mona":       "3692314000005986003",
    "Nency":      "3692314000021764045",
    "Gurleen":    "3692314000011765003",
    "Abhijeet":   "3692314000021796003",
    "Navdeep":    "3692314000019138003",
    "Philpas":    "3692314000017106003",
    "Jashandeep": "3692314000005685243",
    "Jatin":      "3692314000011814003",
    "Ravi":       "3692314000019015149",
    "Ravinder":   "3692314000014190019",
    "Saddam":     "3692314000008763003",
}


def _display_name(zoho_name):
    """Convert a Zoho display_value back to the schedule view's display
    name (Mrunal → Mona). Pass-through when no alias is configured."""
    return _ZOHO_TO_NAME.get(zoho_name, zoho_name)


def _person_json_obj(display_name):
    """{display_value, ID} object for a roster member. Falls back to
    display_value-only when the name isn't in the ID map (so a typo or a
    new hire still saves cleanly to the local DB)."""
    zoho_name = _NAME_TO_ZOHO.get(display_name, display_name)
    zid = _NAME_TO_ZOHO_ID.get(display_name)
    if zid:
        return {"display_value": zoho_name, "ID": zid}
    return {"display_value": zoho_name}


def _fetch_employee_roster():
    return _STAFF_ROSTER


# ---------- Google Maps Distance Matrix (one-way drive minutes) ----------

_WAREHOUSE_ADDRESS = "3600A Laird Rd, Mississauga, ON"


def _fetch_drive_minutes(origin, destination):
    """One-way drive duration (minutes) from origin → destination via the
    Google Maps Distance Matrix API. Returns None on any failure (no key,
    network error, NOT_FOUND, ZERO_RESULTS, etc.) — callers fall back to a
    flat 30-minute estimate so an offline failure doesn't block scheduling.
    """
    if not origin or not destination:
        return None
    key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        return None
    try:
        import httpx
    except Exception:
        return None
    try:
        with httpx.Client(timeout=10.0) as c:
            r = c.get(
                "https://maps.googleapis.com/maps/api/distancematrix/json",
                params={
                    "origins": origin,
                    "destinations": destination,
                    "mode": "driving",
                    "units": "imperial",
                    "key": key,
                },
            )
            data = r.json()
    except Exception:
        return None
    rows = (data or {}).get("rows") or []
    if not rows:
        return None
    elements = rows[0].get("elements") or []
    if not elements:
        return None
    el = elements[0]
    if el.get("status") != "OK":
        return None
    secs = (el.get("duration") or {}).get("value")
    if secs is None:
        return None
    return max(1, round(secs / 60))


def _date_bounds(rows):
    """Earliest / latest scheduled date among the rows, padded so the
    calendar always renders a couple of weeks of context around the data
    (and so today is visible even if the dataset is empty)."""
    earliest, latest = None, None
    for r in rows:
        d = _parse_mdy(r["Coming_Staging_Destaging_Date"])
        if not d:
            continue
        if earliest is None or d < earliest:
            earliest = d
        if latest is None or d > latest:
            latest = d
    today = date.today()
    if earliest is None: earliest = today - timedelta(days=21)
    if latest   is None: latest   = today + timedelta(days=84)
    if today < earliest: earliest = today - timedelta(days=14)
    if today > latest:   latest   = today + timedelta(days=14)
    earliest -= timedelta(days=14)
    latest   += timedelta(days=28)
    return earliest, latest


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
        flex: 0 0 auto;
        display: flex; align-items: center; gap: 12px;
        flex-wrap: nowrap;
        padding: 8px 16px;
        min-height: var(--toolbar-h);
        background: var(--surface); border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow-sm); z-index: 20;
        overflow-x: auto;
    }
    .toolbar-title { font-weight: 700; font-size: 17px; letter-spacing: -0.01em; white-space: nowrap; }
    .toolbar-title .accent { color: var(--accent); }
    .toolbar-spacer { flex: 1; }
    /* In Schedule view, hide the global toolbar's range / search /
       mytasks blocks since the schedule controls live in the chips
       bar below the toolbar. */
    [data-view="schedule"] #range-btn,
    [data-view="schedule"] .search-wrap,
    [data-view="schedule"] #mytasks-btn { display: none; }
    /* Settings sticks to the right of the toolbar regardless of view. */
    .toolbar > button:last-child { margin-left: auto; }
    /* sched-controls (Today, ‹/›, week range, Guide) — left side of
       the page-level chips bar; chips fill the remaining space. */
    .sched-controls {
        display: flex; align-items: center; gap: 6px;
        flex-wrap: nowrap; white-space: nowrap;
        flex-shrink: 0;
    }

    /* unified toolbar button */
    .tbtn {
        all: unset; box-sizing: border-box;
        display: inline-flex; align-items: center; gap: 7px;
        padding: 7px 12px; font-size: 13px; font-weight: 500;
        background: var(--surface); color: var(--text);
        border: 1px solid var(--border); border-radius: var(--radius-md);
        cursor: pointer; transition: all 140ms ease;
        font-family: inherit; white-space: nowrap;
        flex-shrink: 0; max-width: 100%; overflow: hidden;
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
        position: sticky; top: 0; z-index: 4;
        background: var(--accent-soft); color: var(--accent);
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        padding: 6px 14px; font-size: 11px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em;
        white-space: nowrap;
    }
    tr.date-banner td.banner-date {
        font-size: 13px; font-weight: 700; letter-spacing: 0.03em;
        text-transform: none;
    }
    tr.date-banner td.banner-label { opacity: 0.7; }

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
        flex: 0 1 auto; min-width: 0;
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
        text-decoration: none; color: #ea4335;
        transition: all 140ms ease;
    }
    .map-link:hover { background: #fce8e6; color: #d93025; }
    .map-link svg { display: block; }
    .staging-address { font-weight: 600; color: var(--text); margin-top: 2px; }
    .sublinks { display: flex; flex-wrap: nowrap; gap: 6px; margin-top: 8px; min-width: 0; }
    .sublinks .sublink { flex-shrink: 0; }
    .sublink { font-size: 11px; font-weight: 500; padding: 3px 8px; border-radius: var(--radius-sm); background: var(--accent-soft); color: var(--accent); text-decoration: none; transition: background 140ms ease; border: 0; cursor: pointer; font-family: inherit; line-height: inherit; }
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
    .view-seg { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 3px; gap: 2px; flex-shrink: 0; }
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

    .cal-view-scroll {
        flex: 1; overflow: auto; padding: 0 12px 20px; background: var(--bg);
        position: relative;
    }
    .cal-view-dow-row {
        position: sticky; top: 0; z-index: 6;
        display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 6px; background: var(--bg);
        padding: 8px 0 6px;
    }
    .cal-view-dow {
        text-align: center; padding: 4px 0 6px; font-size: 11px;
        font-weight: 600; color: var(--text-faint);
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .cal-week {
        display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 6px; margin-bottom: 6px;
        min-height: var(--week-h, 560px);
    }
    .cal-view-day {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md);
        display: flex; flex-direction: column;
        overflow: hidden; min-height: 0;
        transition: border-color 120ms ease, background 120ms ease;
    }
    .cal-view-day.outside { opacity: 0.55; }

    /* kind-toggle pills in the calendar toolbar */
    .kind-toggles { display: inline-flex; flex-wrap: wrap; gap: 4px; }
    .kind-btn {
        all: unset; box-sizing: border-box; cursor: pointer; font-family: inherit;
        padding: 5px 10px; font-size: 11px; font-weight: 600;
        background: var(--surface-2); color: var(--text-muted);
        border: 1px solid var(--border); border-radius: 999px;
        text-transform: uppercase; letter-spacing: 0.04em;
        transition: all 120ms ease;
    }
    .kind-btn:hover { color: var(--text); border-color: var(--border-strong); }
    .kind-btn.on { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
    .kind-btn[data-kind="Destage"].on      { background: var(--warning-soft); color: var(--warning); border-color: var(--warning); }
    .kind-btn[data-kind="Consultation"].on { background: var(--success-soft); color: var(--success); border-color: var(--success); }
    .kind-btn[data-kind="Design"].on       { background: var(--surface-3); color: var(--text); border-color: var(--border-strong); }
    .cal-view-day.weekend { background: var(--surface-2); }
    .cal-view-day.today { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-soft); }

    .cal-view-day-head {
        display: flex; justify-content: space-between; align-items: center;
        padding: 4px 6px; font-size: 10px; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;
        border-bottom: 1px solid var(--border);
        background: var(--surface);
    }
    .cal-view-day-num { font-size: 13px; font-weight: 700; color: var(--text); }
    .cal-view-day.today .cal-view-day-num,
    .cal-view-day.today .cal-view-day-head { color: var(--accent); }

    .cal-day-expand {
        all: unset; box-sizing: border-box; cursor: pointer;
        padding: 2px; border-radius: 3px; color: var(--text-faint);
        line-height: 0; transition: all 120ms ease;
    }
    .cal-day-expand:hover { color: var(--accent); background: var(--accent-soft); }
    .cal-day-expand svg { width: 12px; height: 12px; display: block; }

    /* slot rows inside each calendar day — 4 team lanes per shift, 8 total.
       AM/PM section headers are intentionally absent; the per-row label
       (AM 1, AM 2, ..., PM 4) carries the indicator. */
    .cal-slots { display: flex; flex-direction: column; flex: 1; min-height: 0; }
    .cal-slot {
        flex: 1 1 0; min-height: 54px;
        display: flex; align-items: stretch; gap: 3px;
        padding: 4px 4px; border-bottom: 1px solid transparent;
        transition: background 120ms ease;
    }
    .cal-slot.am-end { border-bottom: 1px dashed var(--border); }
    .cal-slot.drop-over { background: var(--accent-soft); }
    .cal-slot-time {
        flex: 0 0 32px; font-size: 9px; color: var(--text-faint);
        font-variant-numeric: tabular-nums; line-height: 14px;
        opacity: 0.55; padding-top: 2px;
    }
    .cal-slot-cards { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }

    .cal-cards-source { display: none; }

    .cal-card {
        display: flex; flex-direction: column; gap: 1px;
        padding: 2px 6px; border-radius: 3px;
        background: var(--surface); border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        cursor: grab; font-size: 11px; color: var(--text);
        transition: box-shadow 140ms ease, transform 140ms ease;
        min-width: 0;
    }
    .cal-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
    .cal-card:active { cursor: grabbing; }
    .cal-card.dragging { opacity: 0.4; }
    .cal-card.kind-staging      { border-left-color: var(--accent); }
    .cal-card.kind-destage      { border-left-color: var(--warning); background: var(--warning-soft); }
    .cal-card.kind-consultation { border-left-color: var(--success); background: var(--success-soft); }
    .cal-card.kind-design       { border-left-color: var(--text-muted); background: var(--surface-2); border-style: dashed; }
    .cal-card.state-today { box-shadow: inset 2px 0 0 var(--accent); }

    .cal-card-head {
        display: flex; justify-content: space-between; align-items: center;
        gap: 6px; font-size: 9px; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase; color: var(--text-muted); line-height: 1.1;
    }
    .cal-card.kind-destage .cal-card-head { color: var(--warning); }
    .cal-card.kind-consultation .cal-card-head { color: var(--success); }
    .cal-card-kind { flex-shrink: 0; }
    .cal-card-cust {
        color: var(--text); font-weight: 600; font-size: 10px;
        text-transform: none; letter-spacing: 0;
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        max-width: 60%;
    }
    .cal-card-addr {
        font-weight: 600; color: var(--text); font-size: 11px; line-height: 1.2;
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .cal-card-meta {
        font-size: 9px; color: var(--text-muted); white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
    }

    /* ---------- day detail (full-screen scheduler) ---------- */
    dialog#day-detail.day-modal { max-width: 100vw; width: 100vw; }
    dialog#day-detail.day-modal .modal-card {
        max-height: 100vh; height: 100vh;
        padding: 0; border-radius: 0;
        display: flex; flex-direction: column; overflow: hidden;
    }
    .day-head {
        display: flex; align-items: center; gap: 14px;
        padding: 14px 22px; border-bottom: 1px solid var(--border);
        flex-shrink: 0;
    }
    .day-head .day-title { font-size: 18px; font-weight: 700; letter-spacing: -0.01em; }
    .day-head .day-sub { font-size: 12px; color: var(--text-muted); }
    .day-head .spacer { flex: 1; }
    .day-staff {
        padding: 10px 22px; background: var(--surface-2);
        border-bottom: 1px solid var(--border); flex-shrink: 0;
        display: flex; flex-direction: column; gap: 8px;
    }
    .day-staff-row {
        display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    }
    .day-staff-row-label {
        font-size: 11px; color: var(--text-muted);
        letter-spacing: 0.04em; margin-right: 8px;
        flex: 0 0 auto; min-width: 180px;
    }
    .day-staff-row-label strong {
        font-weight: 700; color: var(--text); text-transform: uppercase;
        font-size: 11px; letter-spacing: 0.06em; margin-right: 6px;
    }
    .day-staff-row-label .hours {
        font-variant-numeric: tabular-nums;
    }
    .day-staff-row-label .note {
        display: block; font-size: 10px; color: var(--text-faint);
        font-style: italic; margin-top: 1px;
    }
    .day-staff-chip {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 10px; border-radius: 999px;
        background: var(--surface); border: 1px solid var(--border);
        font-size: 12px; cursor: grab; user-select: none;
        transition: all 120ms ease;
    }
    .day-staff-chip:hover { border-color: var(--accent); }
    .day-staff-chip:active { cursor: grabbing; }
    .day-staff-chip.disabled { opacity: 0.35; cursor: not-allowed; pointer-events: none; }
    .day-staff-chip .role-tag {
        font-size: 9px; color: var(--text-faint); font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .day-staff-chip[data-role-stager="1"] .role-tag::before { content: 'S'; color: var(--accent); margin-right: 2px; }
    .day-staff-chip[data-role-mover="1"]  .role-tag::after  { content: 'M'; color: var(--warning); margin-left: 2px; }
    .day-staff-chip .load {
        font-size: 10px; color: var(--text-faint);
        font-variant-numeric: tabular-nums; margin-left: 2px;
    }
    .day-staff-chip.maxed { background: var(--surface-3); }

    .day-body { flex: 1; overflow: auto; padding: 16px 22px 24px; }
    .day-cards { display: flex; flex-direction: column; gap: 10px; }
    .day-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md); padding: 14px 16px;
        display: grid; grid-template-columns: 90px 1fr auto; gap: 16px;
        align-items: center;
    }
    .day-card.kind-staging      { border-left: 4px solid var(--accent); }
    .day-card.kind-destage      { border-left: 4px solid var(--warning); }
    .day-card.kind-consultation { border-left: 4px solid var(--success); }
    .day-card.kind-design       { border-left: 4px solid var(--text-muted); border-style: dashed; }

    .day-card-time {
        font-size: 16px; font-weight: 700; color: var(--text);
        font-variant-numeric: tabular-nums;
    }
    .day-card-time .day-card-kind {
        display: block; font-size: 9px; font-weight: 700;
        color: var(--text-muted); text-transform: uppercase;
        letter-spacing: 0.05em; margin-top: 2px;
    }
    .day-card-body { min-width: 0; }
    .day-card-body .day-card-addr {
        font-size: 14px; font-weight: 600; color: var(--text);
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .day-card-body .day-card-meta {
        font-size: 12px; color: var(--text-muted); margin-top: 2px;
    }
    .day-card-body .day-card-cust {
        font-size: 12px; color: var(--text-muted); margin-top: 2px;
    }
    .day-card-slots { display: flex; gap: 8px; }
    .day-card-slot {
        min-width: 150px; padding: 8px 10px; border-radius: var(--radius-sm);
        background: var(--surface-2); border: 1px dashed var(--border-strong);
        font-size: 12px; transition: all 120ms ease;
    }
    .day-card-slot .role {
        font-size: 9px; text-transform: uppercase; color: var(--text-muted);
        letter-spacing: 0.05em; font-weight: 600;
    }
    .day-card-slot .estimate {
        font-size: 10px; color: var(--text-faint);
        font-variant-numeric: tabular-nums;
    }
    .day-card-slot .name {
        display: flex; align-items: center; gap: 6px;
        font-weight: 600; color: var(--text); margin-top: 4px;
        min-height: 18px;
    }
    .day-card-slot.empty .name {
        color: var(--text-faint); font-weight: 500;
        font-style: italic;
    }
    .day-card-slot.drop-over {
        border-style: solid; border-color: var(--accent);
        background: var(--accent-soft);
    }
    .day-card-slot.drop-blocked {
        border-color: var(--danger); background: var(--danger-soft);
    }
    .day-card-slot .name .clear {
        margin-left: auto; cursor: pointer; color: var(--text-faint);
        font-size: 14px; line-height: 1; padding: 0 2px;
    }
    .day-card-slot .name .clear:hover { color: var(--danger); }
    .day-empty { padding: 40px 20px; text-align: center; color: var(--text-muted); }

    /* ---------- procedure doc modal ---------- */
    dialog#procedure-modal.procedure-modal { max-width: min(960px, 96vw); width: 96vw; }
    dialog#procedure-modal .modal-card {
        padding: 0; max-height: 90vh; height: 90vh;
        display: flex; flex-direction: column;
    }
    dialog#procedure-modal .day-head { border-radius: var(--radius-lg) var(--radius-lg) 0 0; }
    .procedure-doc {
        padding: 18px 28px 28px; overflow-y: auto;
        font-size: 14px; line-height: 1.55; color: var(--text);
    }
    .procedure-doc h3 {
        font-size: 14px; font-weight: 700; letter-spacing: 0.02em;
        margin: 22px 0 8px; color: var(--text);
        border-top: 1px solid var(--border); padding-top: 16px;
    }
    .procedure-doc h3:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
    .procedure-doc p, .procedure-doc ul { margin: 8px 0; color: var(--text-muted); }
    .procedure-doc ul { padding-left: 22px; }
    .procedure-doc li { margin-bottom: 4px; }
    .procedure-doc b, .procedure-doc strong { color: var(--text); }
    .procedure-doc code {
        background: var(--surface-2); padding: 1px 5px;
        border-radius: 3px; font-family: 'SF Mono', Menlo, monospace;
        font-size: 12px;
    }
    .proc-table {
        width: 100%; border-collapse: collapse; margin: 8px 0 12px;
        font-size: 13px;
    }
    .proc-table th, .proc-table td {
        padding: 6px 10px; border: 1px solid var(--border);
        text-align: left; color: var(--text);
    }
    .proc-table th {
        background: var(--surface-2); font-weight: 600;
        font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
        color: var(--text-muted);
    }

    /* ---------- Schedule view (daily Gantt) ----------
       Per-day card: hour-only time axis, "Jobs" lane carrying rich job
       cards anchored at start time, then employee rows (first-name only)
       with shift bars and busy markers. No half-hour gridlines.        */
    .sched-grid {
        padding: 16px 16px 24px; display: flex; flex-direction: column;
        gap: 18px;
    }
    /* Mobile: drop the day card's left/right inset so cards use the
       full viewport width. Smaller gap between days too. */
    @media (max-width: 700px) {
        .sched-grid { padding: 8px 0 16px; gap: 10px; }
        .sched-day { border-left: 0; border-right: 0; border-radius: 0; }
        .sched-chips-bar { padding: 6px 8px; gap: 8px; }
    }
    .sched-day {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md);
        /* Always fills the viewport. Axis row + axis-corner stay
           sticky at the top while scrolling through this day. */
        width: 100%;
    }

    .sched-table {
        display: grid;
        grid-template-columns: 100px minmax(0, 1fr);
    }
    /* Hour row: short date in the corner + hour ticks. Sticky so it
       stays at the top of the scroll viewport while the body below
       scrolls. */
    .sched-axis-row {
        display: grid;
        grid-template-columns: 100px minmax(0, 1fr);
        position: sticky; top: 0; z-index: 12;
        background: var(--surface);
    }
    /* Page-level chips bar: schedule controls on the first row, the
       chip list always on the next row below — chip list is too wide
       to comfortably share a row with the controls, and putting it
       below gives it the entire bar width to wrap into. */
    .sched-chips-bar {
        flex: 0 0 auto;
        display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center;
        padding: 8px 16px;
        background: var(--surface);
        border-bottom: 1px solid var(--border);
    }
    /* Chip list always wraps to its own row (flex-basis: 100%) so it
       sits under the schedule controls. Inside, the cascading wrap
       order is:
         decrease 1 → chip list wraps below controls (this).
         decrease 2 → movers group wraps below stagers.
         decrease 3 → last-4-mover sub-group wraps below first-4. */
    .sched-chips {
        display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center;
        flex-basis: 100%; min-width: 0;
    }
    .sched-chip-group {
        display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
    }
    .sched-chip-group-stagers { flex-wrap: nowrap; }
    .sched-chip-subgroup {
        display: flex; flex-wrap: nowrap; gap: 6px; align-items: center;
    }
    .sched-chip {
        display: inline-flex; align-items: center;
        padding: 3px 10px; border-radius: 999px;
        font-size: 11px; font-weight: 600;
        background: var(--surface-2); color: var(--text);
        border: 1px solid var(--border);
        cursor: grab; user-select: none;
        white-space: nowrap;
    }
    .sched-chip:active { cursor: grabbing; }
    .sched-chip.role-stager { background: var(--accent-soft); color: var(--accent); border-color: var(--accent-soft); }
    .sched-chip.role-mover  { background: var(--warning-soft); color: var(--warning); border-color: var(--warning-soft); }

    /* Hour row cells: short date in the corner, hour ticks in axis. */
    .sched-axis-corner, .sched-axis {
        height: 32px;
        background: var(--surface-2);
        border-bottom: 1px solid var(--border);
    }
    .sched-axis-corner {
        grid-column: 1 / 2;
        display: flex; align-items: center; justify-content: center;
        padding: 0 8px;
        font-size: 12px; font-weight: 700; color: var(--text);
    }
    .sched-axis { grid-column: 2 / 3; position: relative; }
    .sched-day.today .sched-axis-corner { background: var(--accent-soft); color: var(--accent); }
    .sched-day.weekend .sched-axis-corner { background: var(--surface-3); }
    .sched-tick {
        position: absolute; top: 0; bottom: 0;
        display: flex; align-items: center;
        font-size: 11px; color: var(--text-muted);
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        padding-left: 4px;
    }

    /* Body. The track-col reserves padding-top = --header-h so each card's
       header element can sit absolutely above row 0 without overlapping
       the rows themselves. The name-col gets the same padding-top so
       employee names line up with their tracks. */
    .sched-name-col {
        grid-column: 1 / 2;
        display: flex; flex-direction: column;
        background: var(--surface);
        padding-top: var(--header-h, 84px);
    }
    .sched-track-col {
        grid-column: 2 / 3;
        position: relative;
        display: flex; flex-direction: column;
        background: var(--surface);
        padding-top: var(--header-h, 84px);
    }
    .sched-track-col.drop-over { background: var(--accent-soft); }

    /* A job is two siblings inside track-col: a header at top:0 (in the
       padding-top zone, above row 0) and a slots box positioned at the
       team's row offsets. They share kind colours so they read as one
       unit. */
    .sched-job-header,
    .sched-job-slots {
        position: absolute;
        /* Floor on width — proportional time-span widths below this
           clamp here, so a short job doesn't render too narrow to read.
           Card can extend past its end-time when this kicks in. */
        min-width: 120px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        z-index: 3;
    }
    .sched-job-header {
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        cursor: grab;
        display: flex; flex-direction: column; gap: 2px;
        padding: 4px 10px;
        font-size: 11px; line-height: 1.2;
        background: linear-gradient(to right, var(--surface), var(--surface-2));
    }
    .sched-job-header:active { cursor: grabbing; }
    .sched-job-header.dragging { opacity: 0.4; }
    .sched-job-header .line.first { display: flex; align-items: center; gap: 6px; }
    .sched-job-header .line.first .time { flex: 1; }
    .sched-edit-btn {
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px;
        background: var(--surface-2); color: var(--text-muted);
        border: 1px solid var(--border); border-radius: 4px;
        cursor: pointer; transition: background 140ms ease, color 140ms ease;
        padding: 0; font-family: inherit;
        flex-shrink: 0;
    }
    .sched-edit-btn svg { width: 13px; height: 13px; display: block; }
    .sched-edit-btn:hover { background: var(--accent-soft); color: var(--accent); border-color: var(--accent-soft); }
    .sched-job-slots {
        border-top: 0;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm);
        display: flex; flex-direction: column;
    }
    /* Kind colours — applied to both pieces so they read as one card. */
    .sched-job-header.kind-staging,      .sched-job-slots.kind-staging      { border-left-color: var(--accent); }
    .sched-job-header.kind-destage,      .sched-job-slots.kind-destage      { border-left-color: var(--warning); }
    .sched-job-header.kind-consultation, .sched-job-slots.kind-consultation { border-left-color: var(--success); }
    .sched-job-header.kind-design,       .sched-job-slots.kind-design       { border-left-color: var(--text-muted); }
    .sched-job-header:hover, .sched-job-slots:hover { box-shadow: var(--shadow-md); }
    /* Card on top of another card at an overlap: dim it so the covered
       card's edges + content show through. Click any card to bring it
       to focus → it becomes the topmost (and gets is-covering applied). */
    .sched-job-header.is-covering,
    .sched-job-slots.is-covering { opacity: 0.72; }
    /* No border on .focused — focus is only meant to pop a *covered* card
       to the front so its content is fully visible. The card that's
       already covering doesn't need any visual badge. */

    /* Header-zone content. Single-line per row by default; long
       addresses clip with ellipsis at the card's right edge. */
    .sched-job-header .line {
        font-size: 11px; font-weight: 500; line-height: 1.25;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sched-job-header .nowrap { white-space: nowrap; }
    /* Time + items + drive — single meta line that wraps as items
       (atoms stay together via .nowrap). When the card is wide enough
       all three sit on one line; when narrow, items+drive can drop
       below the time. */
    .sched-job-header .line.meta {
        font-size: 10px;
        display: flex; flex-wrap: wrap; column-gap: 8px; row-gap: 1px;
        white-space: normal; text-overflow: clip;
    }
    .sched-job-header .line.meta .time { color: var(--text); }
    .sched-job-header .line.meta .item,
    .sched-job-header .line.meta .drive { color: var(--text-muted); }
    /* items + drive stay together as one inline group so the wrap
       break happens between time and items, not between items and
       drive. */
    .sched-job-header .line.meta .item-drive {
        display: inline-flex; gap: 4px; white-space: nowrap;
    }
    .sched-job-header .line.first {
        display: flex; gap: 6px; align-items: center;
    }
    .sched-job-header .line.first .spacer { flex: 1; }
    .sched-job-header .line.first .kind {
        font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
        color: var(--text-muted);
    }
    .sched-job-header.kind-staging      .line.first .kind { color: var(--accent); }
    .sched-job-header.kind-destage      .line.first .kind { color: var(--warning); }
    .sched-job-header.kind-consultation .line.first .kind { color: var(--success); }
    /* Mobile shorthand swap: hide the long "CONSULTATION" label on
       narrow viewports and show the short "CONSULT" label instead. */
    .sched-job-header .kind.kind-short { display: none; }
    @media (max-width: 700px) {
        .sched-job-header.kind-consultation .kind.kind-long  { display: none; }
        .sched-job-header.kind-consultation .kind.kind-short { display: inline; }
    }
    .sched-job-header .line.meta .time {
        font-variant-numeric: tabular-nums;
    }
    .sched-job-header .line.addr {
        font-size: 11px; font-weight: 600; color: var(--text);
    }

    /* Live time indicator while a job is being dragged. The badge sits on
       the time axis of the day under the cursor; ::after extends a faint
       vertical guide down through the rest of the day card so the user
       can see exactly which row the drop will land on. */
    .sched-live-time {
        position: absolute; top: 0; bottom: 0;
        transform: translateX(-50%);
        display: flex; align-items: center;
        padding: 0 7px;
        background: var(--accent); color: var(--accent-fg);
        font-size: 11px; font-weight: 700;
        font-variant-numeric: tabular-nums;
        border-radius: 4px;
        pointer-events: none;
        z-index: 20;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
        white-space: nowrap;
    }
    .sched-live-time::after {
        content: ''; position: absolute;
        top: 100%; left: 50%;
        transform: translateX(-50%);
        width: 2px; height: 1200px;
        background: var(--accent);
        opacity: 0.55;
    }

    /* Slot rows inside the slots-box — one per assigned slot. Flex 1 1 0
       distributes the box height equally so each row aligns with a single
       employee track underneath. */
    .sched-job-slot {
        flex: 1 1 0; min-height: 0;
        display: flex; align-items: center; gap: 5px;
        padding: 0 8px;
        font-size: 11px;
        background: var(--surface);
        border-top: 1px dashed rgba(127, 127, 127, 0.18);
    }
    .sched-job-slot:first-child { border-top: 0; }
    .sched-job-slot.role-stager .badge {
        background: var(--accent-soft); color: var(--accent);
    }
    .sched-job-slot.role-mover .badge {
        background: var(--warning-soft); color: var(--warning);
    }
    .sched-job-slot .badge {
        flex: 0 0 auto; font-size: 9px; font-weight: 700;
        padding: 1px 5px; border-radius: 3px;
        background: var(--surface-2); color: var(--text-muted);
        letter-spacing: 0.04em;
    }
    .sched-job-slot .who {
        flex: 0 1 auto; min-width: 0;
        font-weight: 600; color: var(--text);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        cursor: grab; user-select: none;
    }
    .sched-job-slot.empty .who { flex: 1 1 auto; }
    .sched-job-slot.empty .who {
        color: var(--text-faint); font-style: italic; font-weight: 500;
        cursor: default;
    }
    .sched-job-slot.empty.drop-over {
        background: var(--accent-soft);
    }
    /* × sits inline right after the assignee name. */
    .sched-job-slot .slot-remove {
        all: unset; cursor: pointer; font-family: inherit;
        flex: 0 0 auto;
        padding: 0 4px; border-radius: 3px;
        font-size: 14px; line-height: 1; color: var(--text-faint);
        font-weight: 600;
    }
    .sched-job-slot .slot-remove:hover { color: var(--danger); background: var(--danger-soft); }
    .sched-job-slot.removing { opacity: 0.35; }

    /* Employee rows */
    /* Employee row: name (col 1) + shift bar (col 2) form ONE
       continuous coloured strip per role. The name cell uses a
       ::before block at the same vertical span as the bar
       (top:4 bottom:4), so left and right pieces line up flush at
       the column boundary. Stagers use accent-soft + accent text;
       movers use warning-soft + warning text — same colors as the
       chip bar above. */
    .sched-name {
        position: relative; isolation: isolate;
        padding: 0 10px; font-size: 12px; font-weight: 600;
        display: flex; align-items: center;
        height: var(--row-h, 32px);
        user-select: none;
        color: var(--text);
    }
    /* The role-coloured strip sits behind the name text (z-index: -1
       inside the .sched-name's own stacking context, established by
       `isolation: isolate`). Span at top:4 bottom:4 to match the bar
       height in the next column. */
    .sched-name::before {
        content: ''; position: absolute;
        left: 0; right: 0; top: 4px; bottom: 4px;
        background: transparent;
        z-index: -1;
    }
    .sched-name.role-stager { color: var(--accent); }
    .sched-name.role-mover  { color: var(--warning); }
    .sched-name.role-stager::before { background: var(--accent-soft); }
    .sched-name.role-mover::before  { background: var(--warning-soft); }
    .sched-name.phantom { cursor: default; color: var(--text); }
    .sched-name.phantom::before { background: transparent; }

    .sched-track {
        position: relative;
        height: var(--row-h, 32px);
        background: transparent;
    }
    .sched-track.phantom { background: transparent; }
    .sched-shift-bar {
        position: absolute; top: 4px; bottom: 4px;
        left: 0; right: 0;
        background: var(--surface-2);
        pointer-events: none;
    }
    .sched-track.role-stager .sched-shift-bar { background: var(--accent-soft); }
    .sched-track.role-mover  .sched-shift-bar { background: var(--warning-soft); }
    .sched-busy {
        position: absolute; top: 4px; bottom: 4px;
        border-radius: 2px; pointer-events: none;
        display: flex; align-items: center; justify-content: center;
        font-size: 9px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.04em;
        white-space: nowrap; overflow: hidden;
        padding: 0 3px;
    }
    .sched-busy.kind-drive   {
        background: rgba(127, 127, 127, 0.28); color: var(--text-muted);
    }
    .sched-busy.kind-load    {
        background: rgba(217, 119, 6, 0.45); color: #6b3a04;
    }
    .sched-busy.kind-stage   {
        background: rgba(79, 70, 229, 0.45); color: #1e1b4b;
    }
    .sched-busy.kind-consult {
        background: rgba(5, 150, 105, 0.45); color: #064e3b;
    }
    .sched-busy.kind-design  {
        background: var(--surface-3); color: var(--text-muted);
        border: 1px dashed var(--border-strong);
    }
    :root[data-mode="dark"] .sched-busy.kind-load    { color: #fbd38d; }
    :root[data-mode="dark"] .sched-busy.kind-stage   { color: #c7d2fe; }
    :root[data-mode="dark"] .sched-busy.kind-consult { color: #6ee7b7; }
    @media (prefers-color-scheme: dark) {
        :root:not([data-mode="light"]) .sched-busy.kind-load    { color: #fbd38d; }
        :root:not([data-mode="light"]) .sched-busy.kind-stage   { color: #c7d2fe; }
        :root:not([data-mode="light"]) .sched-busy.kind-consult { color: #6ee7b7; }
    }
    .sched-busy.clipped { opacity: 0.45; }

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
        /* Toolbar stays on one row even on narrow viewports — items
           overflow horizontally (overflow-x: auto on .toolbar). */
        .toolbar { padding: 8px 10px; gap: 8px; }
        .search-wrap { min-width: 0; }
        .range-btn { min-width: 0; }

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


def _procedure_modal():
    """Working doc that anyone can read in the browser. Edit this function
    to revise the procedure — the page rebuilds on next load."""
    return Dialog(
        Div(
            Div(
                H2("Daily Scheduling — Procedure", cls="modal-title"),
                Div(cls="spacer"),
                Button("Close", type="button", cls="tbtn",
                       onclick="TB.closeModal('procedure-modal')"),
                cls="day-head",
            ),
            Div(NotStr("""
<div class="procedure-doc">

<h3>Goal</h3>
<p>Fill every working hour of all 11 schedulable staff (3 stagers + 8 movers) by chaining staging / destaging anchors with consultations, design + decor packing, and revisit-touchup tasks.</p>

<h3>Roster &amp; shift hours</h3>
<ul>
  <li><b>Stagers (3):</b> Mona (Mrunal), Nency, Gurleen — <b>9 AM – 5 PM</b></li>
  <li><b>Movers (8):</b> Abhijeet, Navdeep, Philpas, Jashandeep, Jatin, Ravi, Ravinder, Saddam — <b>8:30 AM – 4:30 PM</b></li>
  <li><b>Sales (board users):</b> Aashika, Clara — assign work; not themselves assigned.</li>
  <li>Start times can drift earlier/later for one-off jobs (e.g. a stager starts at 8 if it's a deal-breaker), but that's the exception, not the day.</li>
</ul>

<h3>Step 1 — Anchor with stagings &amp; destagings</h3>
<p>Stagings and destagings are <b>fixed dates from Zoho</b>. They are the schedule anchors: the team built around them carries through the rest of the day.</p>
<p><b>Crew sizing by item count:</b></p>
<ul>
  <li>≤ 50 items → <b>2 movers</b></li>
  <li>&gt; 50 items → <b>3 movers</b></li>
</ul>
<ul>
  <li><b>Staging team:</b> 1 stager + 2-3 movers</li>
  <li><b>Destaging team:</b> 2-3 movers, no stager</li>
</ul>
<p>The first job of the day can sit in the afternoon (elevator window, customer access, etc).</p>

<h3>Step 2 — Chain a 2nd job onto the same crew</h3>
<p>If a crew finishes a morning job by ~12-1 PM, attach a PM job (another staging or destaging) to the same movers. The intervening "drive back to warehouse" disappears — it becomes "drive to next property" instead.</p>
<p>Stagers <b>don't typically chain</b>. After onsite setup they return to the warehouse for design / packing / consultations.</p>

<h3>Step 3 — Time estimation</h3>
<p>Per-block durations (minutes). The <b>start time</b> on a staging card is when the movers arrive at the property to begin unloading — drive + load happen <i>before</i> that, drive-back <i>after</i>.</p>
<table class="proc-table">
<tr><th>Block</th><th>Stager</th><th>Mover</th></tr>
<tr><td>Load (warehouse)</td><td>—</td><td>max(60, items × 2)</td></tr>
<tr><td>Drive each way</td><td>Driving_Time</td><td>Driving_Time</td></tr>
<tr><td>Onsite staging</td><td><b>90</b> (stays for decor/art)</td><td><b>60</b> (leaves first)</td></tr>
<tr><td>Onsite consult</td><td>120</td><td>—</td></tr>
<tr><td>Onsite destage</td><td>—</td><td>load (= max(60, items × 2))</td></tr>
<tr><td>Unload (back at warehouse)</td><td>—</td><td>load (destages only)</td></tr>
</table>
<p><i>Default 30 min driving when Driving_Time is empty. Google Maps Distance Matrix fills the field on first day-detail / schedule open.</i></p>
<p><b>"Staging duration" on the card = 1.5 h</b> — stagers stay 90 min total (movers leave around the 60-min mark to clear the truck).</p>
<p><b>Totals by job:</b></p>
<table class="proc-table">
<tr><th>Kind</th><th>Stager (min)</th><th>Mover (min)</th></tr>
<tr><td>Staging</td><td>2 × drive + 90</td><td>2 × drive + load + 60</td></tr>
<tr><td>Destaging</td><td>—</td><td>2 × drive + 2 × load</td></tr>
<tr><td>Consultation</td><td>2 × drive + 120</td><td>—</td></tr>
<tr><td>Design + Packing</td><td>120</td><td>—</td></tr>
</table>
<p>If a mover chains a 2nd job, subtract <b>one drive leg</b> — the trip that would have gone "back to warehouse" between the two jobs is replaced by the next "drive to property" and never charged separately.</p>

<h3>Step 4 — Fill stager remainder with prep work</h3>
<p>After a stager's morning staging, their afternoon belongs to:</p>
<ul>
  <li><b>Consultations</b> (existing Inquired records)</li>
  <li><b>Design + decor packing</b> for tomorrow's staging (or Friday's if tomorrow is Sunday)</li>
  <li><b>Revisit / touch-up</b> follow-ups (occasionally)</li>
</ul>

<h3>Step 5 — Fill mover remainder with revisit-touchup tasks</h3>
<p>Movers' empty time is the candidate pool for short revisit / touch-up runs at past-staged properties. Pull those from the Tasks pool when wired.</p>

<h3>Weekend rule</h3>
<ul>
  <li>Saturday + Sunday: <b>manual only</b>. The Suggest button refuses to auto-assign unless explicitly overridden.</li>
  <li>Synthetic Design + Packing cards that would land on Sunday auto-shift to the previous Friday.</li>
</ul>

<h3>Schedule view legend</h3>
<ul>
  <li><b>One section per day</b>; today is highlighted; weekends fade.</li>
  <li><b>Time axis = 8 AM → 5 PM</b>, full hours only (no half-hour ticks).</li>
  <li><b>Jobs lane</b> sits above the employee rows — each card is anchored at its start time, sized to the staging duration, and shows: address · items · drive · staging duration · stager + mover name pills.</li>
  <li><b>Employee rows</b> show the first name only on the left and a horizontal <b>shift bar</b> on the right (stager 9–5, mover 8:30–4:30). Coloured segments inside the bar mark busy minutes; un-coloured stretches are vacant and can take consultations / design / revisit-touchups.</li>
  <li><b>Team-first ordering:</b> employees assigned to the day's first job sit at the top of the column so a 10 AM staging crew (e.g. Mona + Jashan + Jatin) reads as a unit.</li>
  <li><b>Drag a job card</b> horizontally to change its start time (snaps to 30 min).</li>
  <li><b>Drag a name pill</b> out of a job card to remove that staff from the slot.</li>
  <li><b>Drag an employee name</b> from the first column onto a job card to assign or replace.</li>
  <li>⤢ on a day jumps to the day-detail dialog for granular changes.</li>
</ul>

<h3>Improving this doc</h3>
<p>Edit <code>as_webapp/portal_web/staging_task_board.py</code> → <code>_procedure_modal()</code> and reload the page. Keep the table sources of truth in sync with the JS time estimator (<code>estimateMin()</code> + the schedule segment builder).</p>

</div>
            """)),
            cls="modal-card",
        ),
        id="procedure-modal", cls="modal procedure-modal",
    )


def _day_detail_modal():
    """Shell for the full-screen day scheduler. JS fills in title, staff
    strip, and card list when openDay(iso) fires."""
    return Dialog(
        Div(
            Div(
                Div(
                    Span(id="day-title", cls="day-title"),
                    Span(id="day-sub", cls="day-sub"),
                ),
                Div(cls="spacer"),
                Button("Suggest", type="button", cls="tbtn",
                       id="day-suggest-btn", onclick="TB.daySuggest()"),
                Button("Clear all", type="button", cls="tbtn",
                       onclick="TB.dayClearAll()"),
                Button("Close", type="button", cls="tbtn",
                       onclick="TB.closeModal('day-detail')"),
                cls="day-head",
            ),
            Div(id="day-staff", cls="day-staff"),
            Div(
                Div(id="day-cards", cls="day-cards"),
                cls="day-body",
            ),
            cls="modal-card",
        ),
        id="day-detail", cls="modal day-modal",
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
    updated by JS from the client state. The .sched-controls block is
    only visible when data-view=schedule (CSS), and the range / search /
    mytasks buttons are hidden in that view."""
    return Div(
        Div(NotStr("Staging "), Span("Task Board", cls="accent"), cls="toolbar-title"),

        Div(
            Button("Table", type="button",
                   **{"data-view": "table", "onclick": "TB.setView('table')"}),
            Button("Calendar", type="button",
                   **{"data-view": "calendar", "onclick": "TB.setView('calendar')"}),
            Button("Schedule", type="button",
                   **{"data-view": "schedule", "onclick": "TB.setView('schedule')"}),
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

    # Line 2: "0 Remaining / 9 in Design".
    # TODO: "Remaining" = items at warehouse that belong to this staging.
    # Needs a staging→items linkage we don't yet have on this page. Defaulting
    # to 0 (assume items are all on-site) until the Design view ships.
    try:
        in_design = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        in_design = 0
    remaining = 0
    items_line = f"{remaining} Remaining / {in_design} in Design"

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
        pin_svg = (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" '
            'aria-hidden="true"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s'
            '7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-'
            '2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
        )
        addr_children.append(
            A(NotStr(pin_svg), href=maps_url, target="_blank",
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
            Button("Staging", type="button", cls="sublink",
                   onclick=f"StagingEditModal.open('{sid}')"),
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
    # Date banners double as per-group column headers — first cell shows the
    # date instead of "Staging", the rest carry the column labels.
    body = []
    for date_str, group in grouped:
        d = _parse_mdy(date_str)
        d_iso = d.isoformat() if d else ""
        banner_text = d.strftime("%A · %B %-d, %Y") if d else date_str
        if d == date.today():
            banner_text += "  (today)"
        body.append(Tr(
            Td(banner_text, cls="banner-date"),
            Td("Persons", cls="banner-label"),
            Td("Tasks", cls="banner-label"),
            Td("Moving Instructions", cls="banner-label col-moving"),
            Td("General Notes", cls="banner-label col-notes"),
            Td("Accounting", cls="banner-label"),
            Td("Listing", cls="banner-label col-listing"),
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

    return Table(Tbody(*body), cls="board")


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
    cust_first = (row["Customer_First_Name"] or "").strip()
    cust = f"{cust_first} {cust_last}".strip() or "—"
    dd = _parse_mdy(row["Destaging_Date"])
    status = (row["Staging_Status"] or "").strip().lower()
    if status == "inquired":
        kind = "Consultation"
    elif dd and coming == dd:
        kind = "Destage"
    else:
        kind = "Staging"

    try:
        items = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        items = 0
    try:
        driving = int(str(row["Driving_Time"] or "").strip() or "0")
    except Exception:
        driving = 0

    eta = (row["Staging_ETA"] or "").strip()
    if kind == "Consultation":
        cdt = (row["Consultation_Date_and_Time"] or "").strip()
        if " " in cdt:
            eta = cdt.split(" ", 1)[1][:5]  # "HH:MM"
    if not eta:
        eta = "08:00"

    rec = _record_data(row)

    # Stager / mover fields can be either Zoho-synced or local (after a
    # schedule-view save). Apply the alias so "Mrunal" surfaces as "Mona"
    # in the UI without losing identity.
    if kind == "Consultation":
        stager_default = "|".join(
            _display_name(p) for p in _parse_people(row["Consultation_Stager1"])
        )
    else:
        stager_default = "|".join(
            _display_name(p) for p in _parse_people(row["Stager"])
        )
    movers_field = "Destaging_Movers" if kind == "Destage" else "Staging_Movers"
    mover_default = "|".join(
        _display_name(p) for p in _parse_people(row[movers_field])
    )

    return Div(
        Div(
            Span(kind, cls="cal-card-kind"),
            Span(cust, cls="cal-card-cust"),
            cls="cal-card-head",
        ),
        Div(addr, cls="cal-card-addr"),
        Div(f"{eta} · {items} item{'s' if items != 1 else ''}", cls="cal-card-meta"),
        cls=f"cal-card kind-{kind.lower()} {_row_state(row, coming)}",
        draggable="true",
        **{
            "data-record": "cal",
            "data-sid": str(sid),
            "data-date": rec["date_iso"],
            "data-people": rec["people_blob"],
            "data-search": rec["search_blob"],
            "data-kind": kind,
            "data-items": str(items),
            "data-driving": str(driving),
            "data-eta": eta,
            "data-cust": cust,
            "data-addr": addr,
            "data-stager-default": stager_default,
            "data-mover-default": mover_default,
        },
    )


def _build_schedule_view():
    """Schedule pane — top bar with schedule controls (Today, ‹/›,
    week range, Guide) on the left and one shared set of draggable
    stager/mover chips on the right + scroll body. JS renderSchedule()
    fills the body with one section per day; the chip strip is
    populated once on first render."""
    chips_bar = Div(
        Div(
            Button("Today", type="button", cls="tbtn",
                   onclick="TB.schedToday()"),
            Button(NotStr("‹"), type="button", cls="tbtn",
                   onclick="TB.schedShift(-1)", **{"aria-label": "Previous day"}),
            Button(NotStr("›"), type="button", cls="tbtn",
                   onclick="TB.schedShift(1)", **{"aria-label": "Next day"}),
            Div(id="sched-title", cls="cal-view-title"),
            Button("Guide", type="button", cls="tbtn",
                   onclick="TB.openModal('procedure-modal')"),
            cls="sched-controls",
        ),
        Div(id="sched-chips", cls="sched-chips"),
        id="sched-chips-bar", cls="sched-chips-bar",
    )
    scroll = Div(
        Div(id="sched-grid", cls="sched-grid"),
        cls="cal-view-scroll", id="sched-scroll",
    )
    return chips_bar, scroll


def _build_pre_staging_card(row):
    """Synthetic 'Design & Packing' card for the day before each Staging job
    (not for Destages or Consultations). 2 hours of stager work; happens at
    the warehouse, so no driving component."""
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])
    if not coming:
        return None
    dd = _parse_mdy(row["Destaging_Date"])
    status = (row["Staging_Status"] or "").strip().lower()
    if status == "inquired":
        return None
    if dd and coming == dd:
        return None
    pre_date = coming - timedelta(days=1)
    # Skip Sundays — design + packing happens at the warehouse and we don't
    # auto-staff weekends. If staging is Monday, design lands on Sunday →
    # bump back to Friday (staging_date − 3).
    if pre_date.weekday() == 6:
        pre_date -= timedelta(days=2)
    sid = row["ID"]
    addr = _parse_link(row["Staging_Address"]) or row["Staging_Display_Name"] or "—"
    cust_first = (row["Customer_First_Name"] or "").strip()
    cust_last  = (row["Customer_Last_Name"] or "").strip()
    cust = f"{cust_first} {cust_last}".strip() or "—"
    try:
        items = int(str(row["Total_Item_Number"] or 0).split(".")[0])
    except Exception:
        items = 0
    return Div(
        Div(
            Span("Design", cls="cal-card-kind"),
            Span(cust, cls="cal-card-cust"),
            cls="cal-card-head",
        ),
        Div(addr, cls="cal-card-addr"),
        Div(f"design + packing · 2h · {items} items", cls="cal-card-meta"),
        cls="cal-card kind-design",
        draggable="true",
        **{
            "data-record": "cal",
            "data-sid": f"{sid}_dp",
            "data-date": pre_date.isoformat(),
            "data-people": "",
            "data-search": (addr + " " + cust + " design packing").lower(),
            "data-kind": "Design",
            "data-items": str(items),
            "data-driving": "0",
            # Design+Packing is the day's last task — guide stagers to
            # do it after their morning staging / consultation. The
            # actual deadline is midnight of the staging day; this is
            # only a default placement on the timeline.
            "data-eta": "15:00",
            "data-cust": cust,
            "data-addr": addr,
            # Inherit the parent staging's Stager(s) so today's warehouse
            # prep is done by the same people doing tomorrow's onsite
            # work. User can drag-replace from the schedule view.
            "data-stager-default": "|".join(
                _display_name(p) for p in _parse_people(row["Stager"])
            ),
            "data-mover-default": "",
        },
    )


def _build_calendar_view(rows):
    cards = []
    for r in rows:
        if not r["Coming_Staging_Destaging_Date"]:
            continue
        cards.append(_build_calendar_card(r))
        pre = _build_pre_staging_card(r)
        if pre is not None:
            cards.append(pre)
    kind_btns = []
    for slug, label in (("Consultation","Consultation"), ("Design","Design"),
                        ("Staging","Staging"), ("Destage","Destaging"),
                        ("Task","Task")):
        kind_btns.append(Button(
            label, type="button", cls="kind-btn on",
            **{"data-kind": slug, "onclick": f"TB.toggleKind('{slug}')"},
        ))

    toolbar = Div(
        Button("Today", type="button", cls="tbtn", onclick="TB.calViewToday()"),
        Button(NotStr("‹"), type="button", cls="tbtn",
               onclick="TB.calViewShift(-1)", **{"aria-label": "Previous week"}),
        Button(NotStr("›"), type="button", cls="tbtn",
               onclick="TB.calViewShift(1)", **{"aria-label": "Next week"}),
        Div(id="cal-view-title", cls="cal-view-title", style="margin-left:6px"),
        Div(cls="spacer"),
        Div(*kind_btns, cls="kind-toggles"),
        cls="cal-view-toolbar",
    )
    scroll = Div(
        Div(id="cal-view-grid", cls="cal-view-grid"),
        cls="cal-view-scroll",
    )
    source = Div(*cards, id="cal-cards-source", cls="cal-cards-source")
    return toolbar, scroll, source


# -------------------- client JS --------------------

def _client_script(employees, corpus, roster, date_min, date_max):
    # Use JSON embedding so Python string escaping doesn't bite us.
    employees_json = json.dumps(employees)
    corpus_json = json.dumps(corpus[:400])  # cap for sanity
    roster_json = json.dumps(roster)
    date_min_iso = json.dumps(date_min.isoformat())
    date_max_iso = json.dumps(date_max.isoformat())

    return Script(
        # Embed data as JSON strings the JS reads at startup.
        f"window.TB_EMPLOYEES = {employees_json};\n"
        f"window.TB_CORPUS = {corpus_json};\n"
        f"window.TB_ROSTER = {roster_json};\n"
        f"window.TB_DATE_MIN = {date_min_iso};\n"
        f"window.TB_DATE_MAX = {date_max_iso};\n"
        # Main controller — uses template literals so keep regex-free and
        # rely on dict-style keys sparingly.
        r"""
(function() {
    const doc = document.documentElement;
    const K = { THEME:'tb_theme', MODE:'tb_mode', ME:'tb_me', RANGE:'tb_range', MY:'tb_mytasks', VIEW:'tb_view', ASSIGN:'tb_assign' };

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
    const initialView = (storedView === 'calendar' || storedView === 'schedule')
        ? storedView : 'table';

    const state = {
        range: JSON.parse(localStorage.getItem(K.RANGE) || 'null') || PRESETS.week(),
        search: '',
        mytasks: localStorage.getItem(K.MY) === '1',
        me: localStorage.getItem(K.ME) || '',
        view: initialView,
    };

    // Calendar view state. We render every week in the data span; scroll
    // moves through them. The "anchor" is just the week we want at the top
    // of the viewport when calViewToday() / shift fires.
    function sundayOf(d) {
        const x = new Date(d);
        x.setDate(x.getDate() - x.getDay());
        x.setHours(0, 0, 0, 0);
        return x;
    }
    const dateMin = parseIso(window.TB_DATE_MIN) || addDays(today, -28);
    const dateMax = parseIso(window.TB_DATE_MAX) || addDays(today, 84);
    const cal = {
        first: sundayOf(dateMin),
        last:  sundayOf(dateMax),
    };

    // Kind toggle — controls which card kinds render in the calendar grid.
    const KINDS = ['Consultation','Design','Staging','Destage','Task'];
    function loadKinds() {
        try {
            const v = JSON.parse(localStorage.getItem('tb_kinds') || 'null');
            if (v && typeof v === 'object') {
                KINDS.forEach(k => { if (v[k] == null) v[k] = true; });
                return v;
            }
        } catch(_) {}
        const o = {}; KINDS.forEach(k => o[k] = true); return o;
    }
    let kindOn = loadKinds();
    function refreshKindButtons() {
        document.querySelectorAll('.kind-btn').forEach(b => {
            const k = b.dataset.kind;
            b.classList.toggle('on', !!kindOn[k]);
        });
    }
    function toggleKind(k) {
        kindOn[k] = !kindOn[k];
        localStorage.setItem('tb_kinds', JSON.stringify(kindOn));
        refreshKindButtons();
        renderCalendarGrid();
    }

    // Slot helpers — 8 slots per day = 4 team lanes × 2 shifts. AM band is
    // 0-3 (lane 1-4), PM band is 4-7. Slot index represents which team is
    // doing this job, NOT the start hour.  Stager working hours 9-17;
    // mover working hours 8:30-16:30 — used only for capacity headers in
    // the day detail view, not for the calendar slots.
    function etaToBand(eta) {
        if (!eta) return 0;
        const h = parseInt((eta + '').split(':')[0], 10);
        if (isNaN(h)) return 0;
        return h < 12 ? 0 : 4;
    }
    function slotLabel(slot) {
        const band = slot < 4 ? 'AM' : 'PM';
        const idx = (slot % 4) + 1;
        return band + ' ' + idx;
    }
    function slotIsAm(slot) { return slot < 4; }

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
        if (v === 'calendar') {
            renderCalendarGrid();
            // Wait one paint so the now-visible scroll container has a
            // measurable clientHeight before we size the week rows + scroll.
            requestAnimationFrame(() => {
                sizeWeeks();
                scrollToWeekOf(today);
                updateTitleFromScroll();
            });
        } else if (v === 'schedule') {
            ensureChipsBar();
            renderSchedule({ scrollToToday: true });
        }
        applyFilters();
    }

    // ---------- calendar view: grid render ----------
    // Renders every week in [cal.first, cal.last] (the bounded data span).
    // Each week is a `.cal-week` row sized to the viewport so one week fills
    // a screen — vertical scroll moves through past/future weeks. A sticky
    // weekday-header row stays at the top. Cards land in the slot matching
    // their data-slot (last-dropped) or the first empty AM/PM lane based
    // on data-eta. Empty slots stay rendered as drop targets.
    const SVG_EXPAND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14v6h6 M20 10V4h-6 M14 4l6 6 M4 20l6-6"/></svg>';

    function renderCalendarGrid() {
        const grid = document.getElementById('cal-view-grid');
        const src = document.getElementById('cal-cards-source');
        const scrollEl = document.querySelector('#view-calendar .cal-view-scroll');
        if (!grid || !src) return;

        // Park live cards back in source so we can rebuild from scratch.
        grid.querySelectorAll('.cal-card').forEach(c => src.appendChild(c));
        grid.innerHTML = '';

        // Weekday header row (sticky).
        const dowRow = document.createElement('div');
        dowRow.className = 'cal-view-dow-row';
        DOW.forEach(d => {
            const h = document.createElement('div');
            h.className = 'cal-view-dow';
            h.textContent = d;
            dowRow.appendChild(h);
        });
        grid.appendChild(dowRow);

        const slotsByCell = new Map(); // iso -> Map(slotIdx -> .cal-slot-cards div)
        const todayIso = iso(today);
        const nWeeks = Math.max(1, Math.round((cal.last - cal.first) / 86400000 / 7) + 1);

        for (let w = 0; w < nWeeks; w++) {
            const weekStart = new Date(cal.first);
            weekStart.setDate(cal.first.getDate() + w * 7);
            const weekEl = document.createElement('div');
            weekEl.className = 'cal-week';
            weekEl.dataset.weekStart = iso(weekStart);
            for (let i = 0; i < 7; i++) {
                const d = new Date(weekStart);
                d.setDate(weekStart.getDate() + i);
                const cellIso = iso(d);
                const cell = document.createElement('div');
                cell.className = 'cal-view-day';
                cell.dataset.date = cellIso;
                const dow = d.getDay();
                if (dow === 0 || dow === 6) cell.classList.add('weekend');
                if (cellIso === todayIso) cell.classList.add('today');

                const head = document.createElement('div');
                head.className = 'cal-view-day-head';
                const lhs = document.createElement('span');
                lhs.innerHTML = MONTHS[d.getMonth()].slice(0, 3) +
                    ' <span class="cal-view-day-num">' + d.getDate() + '</span>';
                const expand = document.createElement('button');
                expand.type = 'button';
                expand.className = 'cal-day-expand';
                expand.title = 'Expand day · assign staff';
                expand.innerHTML = SVG_EXPAND;
                expand.addEventListener('click', e => {
                    e.stopPropagation();
                    openDay(cellIso);
                });
                head.appendChild(lhs);
                head.appendChild(expand);
                cell.appendChild(head);

                const slots = document.createElement('div');
                slots.className = 'cal-slots';
                const slotMap = new Map();
                for (let s = 0; s < 8; s++) {
                    const row = document.createElement('div');
                    row.className = 'cal-slot' + (s === 3 ? ' am-end' : '');
                    row.dataset.date = cellIso;
                    row.dataset.slot = String(s);
                    const tlabel = document.createElement('span');
                    tlabel.className = 'cal-slot-time';
                    tlabel.textContent = slotLabel(s);
                    const cardsHost = document.createElement('div');
                    cardsHost.className = 'cal-slot-cards';
                    row.appendChild(tlabel);
                    row.appendChild(cardsHost);
                    wireSlotDrop(row);
                    slots.appendChild(row);
                    slotMap.set(s, cardsHost);
                }
                cell.appendChild(slots);
                weekEl.appendChild(cell);
                slotsByCell.set(cellIso, slotMap);
            }
            grid.appendChild(weekEl);
        }

        // Place cards into a slot for their date. Skip cards whose kind has
        // been toggled off. If the user has dragged a card before, respect
        // that pinned slot. Otherwise pick the first empty lane in the AM
        // or PM band based on data-eta.
        Array.from(src.querySelectorAll('.cal-card')).forEach(card => {
            if (!kindOn[card.dataset.kind]) return;
            const d = card.dataset.date;
            const slotMap = slotsByCell.get(d);
            if (!slotMap) return;
            let slotIdx;
            if (card.dataset.slot != null && card.dataset.slot !== '') {
                slotIdx = parseInt(card.dataset.slot, 10);
            } else {
                const band = etaToBand(card.dataset.eta);
                const lanes = band === 0 ? [0,1,2,3] : [4,5,6,7];
                slotIdx = lanes.find(i => {
                    const host = slotMap.get(i);
                    return host && host.children.length === 0;
                });
                if (slotIdx == null) slotIdx = lanes[0];
            }
            const host = slotMap.get(slotIdx) || slotMap.get(0);
            host.appendChild(card);
            wireCardDrag(card);
        });

        // Size each week-row to the visible viewport so one week fills the
        // screen. Re-runs on resize (see DOMContentLoaded wiring below).
        sizeWeeks();
        // Title from current scroll position.
        updateTitleFromScroll();
        applyFilters();
    }

    function sizeWeeks() {
        const scrollEl = document.querySelector('#view-calendar .cal-view-scroll');
        if (!scrollEl) return;
        // Subtract the sticky weekday-header height so each week-row plus
        // the header equals one viewport.
        const dowRow = scrollEl.querySelector('.cal-view-dow-row');
        const dowH = dowRow ? dowRow.offsetHeight : 32;
        const wkH = Math.max(360, scrollEl.clientHeight - dowH - 12);
        scrollEl.style.setProperty('--week-h', wkH + 'px');
    }

    function updateTitleFromScroll() {
        const scrollEl = document.querySelector('#view-calendar .cal-view-scroll');
        const title = document.getElementById('cal-view-title');
        if (!scrollEl || !title) return;
        const weeks = scrollEl.querySelectorAll('.cal-week');
        if (!weeks.length) return;
        const sTop = scrollEl.scrollTop;
        const dowRow = scrollEl.querySelector('.cal-view-dow-row');
        const offset = dowRow ? dowRow.offsetHeight : 0;
        let active = weeks[0];
        weeks.forEach(w => {
            // First week whose top is at-or-above the viewport's content
            // top wins. Iteration is in DOM order so the last one matching
            // is the "topmost visible".
            if (w.offsetTop - offset <= sTop + 4) active = w;
        });
        const ws = parseIso(active.dataset.weekStart);
        if (!ws) return;
        const we = new Date(ws); we.setDate(we.getDate() + 6);
        const sameYear = ws.getFullYear() === we.getFullYear();
        title.textContent = fmt(ws) + ' – ' + fmt(we) +
            (sameYear ? ', ' + we.getFullYear()
                      : ' ' + ws.getFullYear() + ' – ' + we.getFullYear());
    }

    function scrollToWeekOf(d) {
        const scrollEl = document.querySelector('#view-calendar .cal-view-scroll');
        if (!scrollEl) return;
        const target = iso(sundayOf(d));
        const wk = scrollEl.querySelector('.cal-week[data-week-start="' + target + '"]');
        if (!wk) return;
        const dowRow = scrollEl.querySelector('.cal-view-dow-row');
        const offset = dowRow ? dowRow.offsetHeight : 0;
        scrollEl.scrollTop = wk.offsetTop - offset;
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
    function wireSlotDrop(row) {
        row.addEventListener('dragover', e => {
            if (!draggedCard) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            row.classList.add('drop-over');
        });
        row.addEventListener('dragleave', () => row.classList.remove('drop-over'));
        row.addEventListener('drop', e => {
            e.preventDefault();
            row.classList.remove('drop-over');
            if (!draggedCard) return;
            const newDate = row.dataset.date;
            const newSlot = parseInt(row.dataset.slot, 10);
            draggedCard.dataset.date = newDate;
            draggedCard.dataset.slot = String(newSlot);
            const host = row.querySelector('.cal-slot-cards') || row;
            host.appendChild(draggedCard);
        });
    }

    // ---------- calendar: navigation ----------
    function calViewShift(delta) {
        // Scroll the existing rendered grid by one week. Past/future weeks
        // are already in the DOM so this is a pure scrollBy — no re-render.
        const scrollEl = document.querySelector('#view-calendar .cal-view-scroll');
        if (!scrollEl) return;
        const wkH = parseInt(getComputedStyle(scrollEl).getPropertyValue('--week-h'), 10) || 480;
        scrollEl.scrollBy({ top: delta * wkH, behavior: 'smooth' });
    }
    function calViewToday() { scrollToWeekOf(today); }

    // ---------- day detail (full-screen scheduler) ----------
    // Per-day staffing lives client-side. Persisted in localStorage as
    //   { "2026-04-25": { "<staging_id>": { stager: "...", mover: "..." } } }
    // No DB write yet — wire to a POST endpoint when the API is ready.
    const ROSTER = window.TB_ROSTER || [];
    const DAY_CAP_MIN = 480; // 8h capacity per employee per day
    let dayCurrent = null;   // ISO of the day currently open

    function loadAssign() {
        try { return JSON.parse(localStorage.getItem(K.ASSIGN) || '{}'); }
        catch(_) { return {}; }
    }
    function saveAssign(all) {
        localStorage.setItem(K.ASSIGN, JSON.stringify(all));
    }
    function getDayAssign(dIso) {
        const all = loadAssign();
        return all[dIso] || {};
    }
    function setDayAssign(dIso, m) {
        const all = loadAssign();
        all[dIso] = m;
        saveAssign(all);
    }

    // Time estimate (minutes) for one role on one card. The mover for a
    // staging job carries: drive + load + drive + unload + onsite_setup.
    // The stager: drive + onsite_setup. Destage drops the onsite step.
    // Consultation: drive + onsite_consult. Driving_Time falls back to 30.
    // Onsite staging defaults — see procedure doc. Movers leave first (~60
    // min) so they can return to the warehouse for the next load; stagers
    // stay through detail work (decor + art).
    const STAGE_ONSITE_MOVER = 60;
    const STAGE_ONSITE_STAGER = 90;
    // Visual onsite duration that drives the card's rendered width.
    // Kept in sync with the `dur` switch in appendJobToTrack so the
    // busy-marker post-render pass can find each card's right edge.
    function cardDurMin(card) {
        const kind = card.dataset.kind;
        const items = parseInt(card.dataset.items || '0', 10);
        if (kind === 'Staging')      return STAGE_ONSITE_STAGER;
        if (kind === 'Destage')      return Math.max(60, items * 2);
        if (kind === 'Consultation') return CONSULT_ONSITE;
        if (kind === 'Design')       return DESIGN_ONSITE;
        return 90;
    }
    const CONSULT_ONSITE = 120;
    const DESIGN_ONSITE = 120;

    function estimateMin(card, role) {
        const items = parseInt(card.dataset.items || '0', 10);
        const drvOne = parseInt(card.dataset.driving || '0', 10) || 30;
        const driveRound = drvOne * 2;
        const load = Math.max(60, items * 2);
        const kind = card.dataset.kind;
        // Design+Packing happens at the warehouse — no driving component.
        if (kind === 'Design')       return DESIGN_ONSITE;
        if (kind === 'Consultation') return driveRound + CONSULT_ONSITE;
        if (kind === 'Destage')      return driveRound + load + load;
        if (role === 'stager')       return driveRound + STAGE_ONSITE_STAGER;
        return driveRound + load + STAGE_ONSITE_MOVER; // staging mover
    }

    function fmtMin(m) {
        if (!m) return '0m';
        const h = Math.floor(m / 60);
        const mm = m % 60;
        if (!h) return mm + 'm';
        if (!mm) return h + 'h';
        return h + 'h ' + mm + 'm';
    }

    function cardsForDay(dIso) {
        return Array.from(document.querySelectorAll('.cal-card[data-record="cal"]'))
            .filter(c => c.dataset.date === dIso)
            .sort((a, b) => {
                const sa = (a.dataset.slot != null && a.dataset.slot !== '')
                    ? parseInt(a.dataset.slot, 10) : etaToBand(a.dataset.eta);
                const sb = (b.dataset.slot != null && b.dataset.slot !== '')
                    ? parseInt(b.dataset.slot, 10) : etaToBand(b.dataset.eta);
                if (sa !== sb) return sa - sb;
                return (a.dataset.eta || '').localeCompare(b.dataset.eta || '');
            });
    }

    // Slots a card needs by role: staging→stager+mover, destage→mover only,
    // consultation→stager only, design+packing→stager only.
    function rolesForKind(kind) {
        if (kind === 'Destage')      return ['mover'];
        if (kind === 'Consultation') return ['stager'];
        if (kind === 'Design')       return ['stager'];
        return ['stager', 'mover'];
    }

    function crewSize(items) { return (items > 50) ? 3 : 2; }

    // slotsForCard / unfilledSlots are the unified slot iterator used by
    // both the day-detail dialog and the Schedule view. Both stagers and
    // movers are stored as arrays so the user can drop an extra of either
    // role onto a card and that extra slot stays until removed. Default
    // crew (1 stager + 2/3 movers for Staging; 1 stager for Consultation/
    // Design; 2/3 movers for Destage) is the minimum slot count.
    function readStagers(a) {
        if (Array.isArray(a.stagers)) return a.stagers.slice();
        if (a.stager) return [a.stager];
        return [];
    }
    function readMovers(a) {
        if (Array.isArray(a.movers)) return a.movers.slice();
        if (a.mover) return [a.mover];
        return [];
    }
    function slotsForCard(card) {
        const kind = card.dataset.kind;
        const items = parseInt(card.dataset.items || '0', 10);
        const m = getDayAssign(card.dataset.date);
        const a = m[card.dataset.sid] || {};
        const out = [];
        const stagerArr = readStagers(a);
        const movArr = readMovers(a);
        const moverCount = Math.max(crewSize(items), movArr.length);
        // Staging/Consultation/Design default to 1 stager; extras grow
        // the array (and shrink back when removed past the default).
        const stagerCount = Math.max(1, stagerArr.length);
        if (kind === 'Staging') {
            for (let i = 0; i < stagerCount; i++) {
                out.push({ role:'stager', index: i, filled: stagerArr[i] || null });
            }
            for (let i = 0; i < moverCount; i++) {
                out.push({ role:'mover', index: i, filled: movArr[i] || null });
            }
        } else if (kind === 'Destage') {
            for (let i = 0; i < moverCount; i++) {
                out.push({ role:'mover', index: i, filled: movArr[i] || null });
            }
        } else if (kind === 'Consultation' || kind === 'Design') {
            for (let i = 0; i < stagerCount; i++) {
                out.push({ role:'stager', index: i, filled: stagerArr[i] || null });
            }
        }
        return out;
    }
    function unfilledSlots(card) {
        return slotsForCard(card).filter(s => !s.filled);
    }
    function isAssignedTo(card, name, role) {
        return slotsForCard(card).some(s =>
            s.role === role && s.filled === name);
    }

    function dayLoadFor(name, dIso) {
        // Sum estimated minutes for every assignment of `name` on dIso.
        let total = 0;
        cardsForDay(dIso).forEach(card => {
            slotsForCard(card).forEach(s => {
                if (s.filled === name) total += estimateMin(card, s.role);
            });
        });
        return total;
    }

    function setSlotAssign(dIso, sid, role, index, name) {
        const m = getDayAssign(dIso);
        if (!m[sid]) m[sid] = {};
        const writeRoleArray = (arrKey, legacyKey) => {
            let arr = Array.isArray(m[sid][arrKey]) ? m[sid][arrKey].slice()
                    : (m[sid][legacyKey] ? [m[sid][legacyKey]] : []);
            if (name == null) {
                arr.splice(index, 1);
            } else {
                while (arr.length <= index) arr.push(null);
                arr[index] = name;
            }
            arr = arr.filter(x => x);
            if (arr.length) m[sid][arrKey] = arr;
            else delete m[sid][arrKey];
            delete m[sid][legacyKey];
        };
        if (role === 'stager') writeRoleArray('stagers', 'stager');
        else                   writeRoleArray('movers',  'mover');
        // Snapshot the new state BEFORE we possibly delete the entry, so
        // we can persist `[]` to clear the column when the user empties
        // a slot.
        const snapshot = {
            stagers: (m[sid].stagers || []).slice(),
            movers:  (m[sid].movers  || []).slice(),
        };
        if (!snapshot.stagers.length && !snapshot.movers.length) delete m[sid];
        setDayAssign(dIso, m);
        persistAssignment(dIso, sid, snapshot);
    }

    // Fire a save POST so the assignment lands in Staging_Report. Skips
    // synthetic Design+Packing cards (no DB row to write) and silently
    // tolerates network errors — localStorage still has the change.
    function persistAssignment(dIso, sid, snapshot) {
        if (!sid || sid.endsWith('_dp')) return;
        const card = document.querySelector('.cal-card[data-sid="' + sid + '"]');
        if (!card) return;
        const kind = card.dataset.kind;
        if (kind === 'Design') return;
        const fd = new FormData();
        fd.append('sid', sid);
        fd.append('kind', kind);
        fd.append('stagers', (snapshot.stagers || []).join('|'));
        fd.append('movers',  (snapshot.movers  || []).join('|'));
        fetch('/staging_task_board/save_assignment', {
            method: 'POST', body: fd,
        }).catch(() => {});
    }

    // On page load, seed tb_assign from each card's data-*-default
    // attributes (DB state) so the schedule view shows the current
    // Staging_Report assignments. Local edits afterwards overwrite
    // localStorage and POST back to the DB.
    function seedAssignmentsFromDefaults() {
        const all = {};
        document.querySelectorAll('.cal-card[data-record="cal"]').forEach(card => {
            const date = card.dataset.date;
            const sid = card.dataset.sid;
            if (!date || !sid) return;
            if (!all[date]) all[date] = {};
            const stagersStr = (card.dataset.stagerDefault || '').trim();
            const moversStr  = (card.dataset.moverDefault  || '').trim();
            const stagers = stagersStr ? stagersStr.split('|').filter(Boolean) : [];
            const movers  = moversStr  ? moversStr.split('|').filter(Boolean)  : [];
            const obj = {};
            if (stagers.length) obj.stagers = stagers;
            if (movers.length)  obj.movers  = movers;
            if (Object.keys(obj).length) all[date][sid] = obj;
        });
        saveAssign(all);
    }

    function staffCanRole(staff, role) {
        return (staff.roles || []).includes(role);
    }

    function openDay(dIso) {
        dayCurrent = dIso;
        const d = parseIso(dIso);
        const titleEl = document.getElementById('day-title');
        const subEl = document.getElementById('day-sub');
        if (titleEl) titleEl.textContent = d.toLocaleDateString('en-US',
            { weekday:'long', month:'long', day:'numeric', year:'numeric' });
        const cards = cardsForDay(dIso);
        if (subEl) subEl.textContent = '· ' + cards.length + ' job' +
            (cards.length !== 1 ? 's' : '');
        renderDayCards();
        renderStaffStrip();
        openModal('day-detail');
        fillMissingDriving(dIso);
    }

    // POST any cards that haven't got a Driving_Time yet and refresh the
    // detail view when the API returns. Pre-staging Design cards (sid ends
    // in _dp) and synthetic kinds skip the call — they have no warehouse
    // drive component.
    function fillMissingDriving(dIso) {
        const cards = cardsForDay(dIso).filter(c =>
            c.dataset.kind !== 'Design' &&
            !c.dataset.sid.includes('_') &&
            !(parseInt(c.dataset.driving || '0', 10) > 0)
        );
        if (!cards.length) return;
        const sids = cards.map(c => c.dataset.sid).join(',');
        const fd = new FormData();
        fd.append('sids', sids);
        fetch('/staging_task_board/fill_driving', { method: 'POST', body: fd })
            .then(r => r.ok ? r.json() : null)
            .then(j => {
                if (!j || !j.results) return;
                let touched = false;
                cards.forEach(c => {
                    const m = j.results[c.dataset.sid];
                    if (m && m > 0) {
                        c.dataset.driving = String(m);
                        touched = true;
                    }
                });
                if (touched && dIso === dayCurrent) {
                    renderDayCards();
                    renderStaffStrip();
                }
            })
            .catch(() => {});
    }

    // Standard shift hours. Start times can drift earlier/later for one-off
    // jobs, so this is just a guide rendered above the chips — not a hard
    // constraint on the suggest button or drag-drop.
    const SHIFT = {
        stager: { label: 'Stagers', hours: '9 AM – 5 PM' },
        mover:  { label: 'Movers',  hours: '8:30 AM – 4:30 PM' },
    };

    function _buildStaffChip(s) {
        const chip = document.createElement('div');
        chip.className = 'day-staff-chip';
        chip.draggable = true;
        chip.dataset.name = s.name;
        chip.dataset.roles = (s.roles || []).join(',');
        if (staffCanRole(s, 'stager')) chip.dataset.roleStager = '1';
        if (staffCanRole(s, 'mover'))  chip.dataset.roleMover  = '1';
        const tag = document.createElement('span');
        tag.className = 'role-tag';
        chip.appendChild(tag);
        const nm = document.createElement('span');
        nm.textContent = s.name;
        chip.appendChild(nm);
        const load = document.createElement('span');
        load.className = 'load';
        const used = dayLoadFor(s.name, dayCurrent);
        load.textContent = fmtMin(used) + '/' + fmtMin(DAY_CAP_MIN);
        chip.appendChild(load);
        if (used >= DAY_CAP_MIN) {
            chip.classList.add('disabled');
            chip.classList.add('maxed');
            chip.draggable = false;
        }
        chip.addEventListener('dragstart', e => {
            e.dataTransfer.effectAllowed = 'copy';
            try {
                e.dataTransfer.setData('text/plain',
                    JSON.stringify({ name: s.name, roles: s.roles }));
            } catch(_) {}
        });
        return chip;
    }

    function renderStaffStrip() {
        const host = document.getElementById('day-staff');
        if (!host) return;
        host.innerHTML = '';
        const stagers = ROSTER.filter(s => s.roles.includes('stager'));
        const movers  = ROSTER.filter(s => s.roles.includes('mover'));
        function buildRow(roleKey, list) {
            if (!list.length) return;
            const row = document.createElement('div');
            row.className = 'day-staff-row';
            const lbl = document.createElement('span');
            lbl.className = 'day-staff-row-label';
            const cfg = SHIFT[roleKey];
            lbl.innerHTML = '<strong>' + cfg.label + '</strong>' +
                '<span class="hours">' + cfg.hours + '</span>' +
                '<span class="note">flexible — adjust per job</span>';
            row.appendChild(lbl);
            list.forEach(s => row.appendChild(_buildStaffChip(s)));
            host.appendChild(row);
        }
        buildRow('stager', stagers);
        buildRow('mover',  movers);
    }

    function renderDayCards() {
        const host = document.getElementById('day-cards');
        if (!host) return;
        host.innerHTML = '';
        const cards = cardsForDay(dayCurrent);
        if (!cards.length) {
            host.innerHTML = '<div class="day-empty">No stagings or consultations on this day.</div>';
            return;
        }
        cards.forEach(card => {
            const sid = card.dataset.sid;
            const kind = card.dataset.kind;
            const eta = card.dataset.eta ||
                (parseInt(card.dataset.slot || '0', 10) < 4 ? '09:00' : '13:00');
            const wrap = document.createElement('div');
            wrap.className = 'day-card kind-' + kind.toLowerCase();
            wrap.dataset.sid = sid;

            const timeEl = document.createElement('div');
            timeEl.className = 'day-card-time';
            timeEl.innerHTML = eta + '<span class="day-card-kind">' + kind + '</span>';
            wrap.appendChild(timeEl);

            const body = document.createElement('div');
            body.className = 'day-card-body';
            const items = parseInt(card.dataset.items || '0', 10);
            const drv = parseInt(card.dataset.driving || '0', 10);
            // Total = sum of every slot's per-role estimate (so a destage
            // with 3 movers shows ~3× mover hours).
            const total = slotsForCard(card)
                .reduce((acc, s) => acc + estimateMin(card, s.role), 0);
            body.innerHTML =
                '<div class="day-card-addr">' + escapeHtml(card.dataset.addr) + '</div>' +
                '<div class="day-card-cust">' + escapeHtml(card.dataset.cust || '') + '</div>' +
                '<div class="day-card-meta">' +
                    items + ' item' + (items !== 1 ? 's' : '') +
                    ' · drive ' + (drv || 30) + 'm each way' +
                    ' · total est ' + fmtMin(total) +
                    ((kind === 'Staging' || kind === 'Destage')
                        ? ' · crew ' + crewSize(items) + ' movers' : '') +
                '</div>';
            wrap.appendChild(body);

            const slotsHost = document.createElement('div');
            slotsHost.className = 'day-card-slots';
            slotsForCard(card).forEach(s => {
                const slot = document.createElement('div');
                slot.className = 'day-card-slot' + (s.filled ? '' : ' empty');
                slot.dataset.role = s.role;
                slot.dataset.sid = sid;
                slot.dataset.index = String(s.index);
                const est = estimateMin(card, s.role);
                const roleLabel = (s.role === 'mover' && (kind === 'Staging' || kind === 'Destage'))
                    ? ('mover ' + (s.index + 1)) : s.role;
                slot.innerHTML =
                    '<div class="role">' + roleLabel + ' · ' + fmtMin(est) + '</div>' +
                    '<div class="name">' + (s.filled
                        ? escapeHtml(s.filled) + '<span class="clear" data-action="clear">×</span>'
                        : 'Drag staff here') + '</div>';
                wireSlotDrop2(slot);
                slotsHost.appendChild(slot);
            });
            wrap.appendChild(slotsHost);
            host.appendChild(wrap);
        });
        host.querySelectorAll('[data-action="clear"]').forEach(b => {
            b.addEventListener('click', e => {
                e.stopPropagation();
                const slotEl = b.closest('.day-card-slot');
                setSlotAssign(dayCurrent, slotEl.dataset.sid,
                    slotEl.dataset.role,
                    parseInt(slotEl.dataset.index || '0', 10),
                    null);
                renderDayCards();
                renderStaffStrip();
            });
        });
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
    }

    function wireSlotDrop2(slot) {
        slot.addEventListener('dragover', e => {
            e.preventDefault();
            slot.classList.add('drop-over');
            e.dataTransfer.dropEffect = 'copy';
        });
        slot.addEventListener('dragleave', () => {
            slot.classList.remove('drop-over', 'drop-blocked');
        });
        slot.addEventListener('drop', e => {
            e.preventDefault();
            slot.classList.remove('drop-over', 'drop-blocked');
            let payload = null;
            try { payload = JSON.parse(e.dataTransfer.getData('text/plain') || ''); }
            catch(_) {}
            if (!payload || !payload.name) return;
            const role = slot.dataset.role;
            const roles = payload.roles || [];
            if (!roles.includes(role)) return;
            const idx = parseInt(slot.dataset.index || '0', 10);
            setSlotAssign(dayCurrent, slot.dataset.sid, role, idx, payload.name);
            renderDayCards();
            renderStaffStrip();
        });
    }

    let _dragRoles = null;
    function staffDragOk(role) {
        // Without dragover access to dataTransfer.types in all browsers, we
        // optimistically allow; the drop handler enforces strict role match.
        return true;
    }

    function daySuggest() {
        // Greedy fill: for each card slot in start-time order, pick the
        // staff with matching role and smallest current load (and capacity
        // remaining for the slot's estimate). Show a confirm before applying.
        // Weekends are off-limits to auto-assign — Saturday/Sunday work
        // happens by exception, so the user has to explicitly opt in.
        const dObj = parseIso(dayCurrent);
        const dow = dObj ? dObj.getDay() : -1;
        if (dow === 0 || dow === 6) {
            const which = dow === 0 ? 'Sunday' : 'Saturday';
            if (!confirm(which + ' — auto-assign is off by default for ' +
                'weekends. Run Suggest anyway?')) return;
        }
        const cards = cardsForDay(dayCurrent);
        // Working copy of loads so estimates compound correctly across picks.
        const load = {};
        ROSTER.forEach(s => { load[s.name] = dayLoadFor(s.name, dayCurrent); });
        const picks = []; // {sid, role, index, name, est}
        cards.forEach(card => {
            const sid = card.dataset.sid;
            // Pick across every empty slot (stager + N movers); skip slots
            // that already have someone.
            unfilledSlots(card).forEach(s => {
                const est = estimateMin(card, s.role);
                const candidates = ROSTER
                    .filter(st => staffCanRole(st, s.role))
                    .filter(st => !picks.some(p =>
                        p.sid === sid && p.name === st.name)) // no double-pick on same card
                    .filter(st => load[st.name] + est <= DAY_CAP_MIN)
                    .sort((a, b) => load[a.name] - load[b.name]
                                   || a.name.localeCompare(b.name));
                if (!candidates.length) return;
                const pick = candidates[0];
                load[pick.name] += est;
                picks.push({ sid, role: s.role, index: s.index,
                            name: pick.name, est });
            });
        });
        if (!picks.length) {
            alert('Nothing to suggest — every job is already filled (or the roster is empty / at capacity).');
            return;
        }
        const summary = picks.map(p => {
            const card = document.querySelector('.cal-card[data-sid="' + p.sid + '"]');
            const where = card ? (card.dataset.addr || card.dataset.cust || '') : '';
            return '• ' + p.role + ' → ' + p.name + ' (' + (where || p.sid) + ')';
        }).join('\n');
        if (!confirm('Auto-assign ' + picks.length + ' slot' + (picks.length !== 1 ? 's' : '') + '?\n\n' + summary)) return;
        picks.forEach(p => {
            setSlotAssign(dayCurrent, p.sid, p.role, p.index, p.name);
        });
        renderDayCards();
        renderStaffStrip();
    }

    function dayClearAll() {
        if (!confirm('Clear all assignments for this day?')) return;
        setDayAssign(dayCurrent, {});
        renderDayCards();
        renderStaffStrip();
    }

    // ---------- Schedule view (daily timeline) ----------
    // Daily Gantt: rows = 11 schedulable employees (stagers first, movers
    // below), columns = 8:30 AM → 5 PM. Each card on the day translates
    // into a sequence of role-specific segments (load → drive → stage →
    // drive back, etc.) drawn into the assignee's row. Cards lacking a
    // role show up in the day's "Unassigned" strip.

    // Timeline 8 AM – 5 PM (full hour ticks). Mover shift = 8:30–4:30
    // (offsets 30..510). Stager shift = 9–5 (60..540).
    // Timeline starts at 8:30 AM (the start of every shift) so the
    // axis has no dead 8:00–8:30 gap before the first activity.
    const SCHED_START_MIN = 8 * 60 + 30;     // 8:30 AM
    const SCHED_END_MIN   = 17 * 60;         // 5:00 PM
    const SCHED_DUR       = SCHED_END_MIN - SCHED_START_MIN; // 510
    // Both stagers and movers cover the full timeline.
    const SHIFT_MOVER  = { start: 0, end: SCHED_DUR };
    const SHIFT_STAGER = { start: 0, end: SCHED_DUR };

    let schedAnchor = new Date(today);
    // Last card the user clicked on — gets z-index 50 so it pops to the
    // front. Stays sticky across re-renders so drag-drop doesn't blow
    // away the focus.
    let _focusedSid = null;

    function timeToOffset(hhmm) {
        if (!hhmm || typeof hhmm !== 'string') return 0;
        const m = hhmm.match(/^(\d{1,2}):(\d{2})/);
        if (!m) return 0;
        return parseInt(m[1], 10) * 60 + parseInt(m[2], 10) - SCHED_START_MIN;
    }
    function fmtAbs(min) {
        const total = Math.round(min) + SCHED_START_MIN;
        const h = Math.floor(total / 60);
        const mm = total % 60;
        const ampm = h < 12 ? 'AM' : 'PM';
        const h12 = h % 12 === 0 ? 12 : h % 12;
        return mm === 0 ? (h12 + ampm) : (h12 + ':' + String(mm).padStart(2,'0') + ampm);
    }

    // Build the time segments for one role on one card. Returns minutes
    // since SCHED_START_MIN (negative = before 8:30, > SCHED_DUR = after
    // 5 PM; the renderer clips and adds a `clipped` class).
    function buildSegments(card, role) {
        const items = parseInt(card.dataset.items || '0', 10);
        const drv = parseInt(card.dataset.driving || '0', 10) || 30;
        const load = Math.max(60, items * 2);
        const kind = card.dataset.kind;
        const eta = card.dataset.eta || (etaToBand(card.dataset.eta) === 0 ? '09:00' : '13:00');
        const etaMin = timeToOffset(eta);

        if (kind === 'Design') {
            const startMin = 60; // 9 AM default for warehouse design+pack
            return [{ kind:'design', start: startMin, dur: DESIGN_ONSITE,
                      label: 'Design+Pack', sub: card.dataset.cust || '' }];
        }
        if (kind === 'Consultation') {
            return [
                { kind:'drive',   start: etaMin - drv,                dur: drv, label: 'Drive',      sub: card.dataset.addr },
                { kind:'consult', start: etaMin,                       dur: CONSULT_ONSITE, label: 'Consult', sub: card.dataset.cust },
                { kind:'drive',   start: etaMin + CONSULT_ONSITE,     dur: drv, label: 'Drive back', sub: '' },
            ];
        }
        if (kind === 'Destage') {
            // Mover only. Drive to property → load → drive to warehouse → unload.
            return [
                { kind:'drive', start: etaMin - drv,            dur: drv,  label: 'Drive',  sub: card.dataset.addr },
                { kind:'load',  start: etaMin,                  dur: load, label: 'Load',   sub: items + ' items' },
                { kind:'drive', start: etaMin + load,           dur: drv,  label: 'Drive',  sub: 'to warehouse' },
                { kind:'load',  start: etaMin + load + drv,     dur: load, label: 'Unload', sub: '' },
            ];
        }
        // Staging
        if (role === 'stager') {
            return [
                { kind:'drive', start: etaMin - drv,                       dur: drv, label: 'Drive', sub: card.dataset.addr },
                { kind:'stage', start: etaMin,                              dur: STAGE_ONSITE_STAGER, label: 'Stage', sub: card.dataset.cust },
                { kind:'drive', start: etaMin + STAGE_ONSITE_STAGER,        dur: drv, label: 'Drive', sub: 'back' },
            ];
        }
        // Staging mover — leaves earlier than the stager. The card is
        // sized to STAGE_ONSITE_STAGER, so we render the mover's
        // drive-back just past the card's right edge (rather than at
        // the mover's true earlier finish time, which would sit hidden
        // inside the card slot).
        return [
            { kind:'load',  start: etaMin - drv - load, dur: load, label: 'Load',  sub: items + ' items' },
            { kind:'drive', start: etaMin - drv,        dur: drv,  label: 'Drive', sub: card.dataset.addr },
            { kind:'stage', start: etaMin,              dur: STAGE_ONSITE_MOVER, label: 'Unload', sub: '' },
            { kind:'drive', start: etaMin + STAGE_ONSITE_STAGER, dur: drv, label: 'Drive', sub: 'back' },
        ];
    }

    function schedShift(delta) {
        const d = new Date(schedAnchor);
        d.setDate(d.getDate() + delta);
        schedAnchor = d;
        renderSchedule();
    }
    function schedToday() {
        schedAnchor = new Date(today);
        renderSchedule({ scrollToToday: true });
    }

    // Track payload of the currently-dragged item so dragend can detect
    // "dropped outside any target" → remove name pill.
    let _schedDragPayload = null;

    function clipSegment(s0, s1) {
        const clipped = (s0 < 0) || (s1 > SCHED_DUR);
        return { s0: Math.max(0, s0), s1: Math.min(SCHED_DUR, s1), clipped };
    }

    // Row height (px) — every employee track and every internal job slot
    // shares this so they line up. Larger than typical body line-height
    // so name + shift bar feel like one chunky horizontal stripe.
    const ROW_H = 32;
    // Header zone height above row 0. HEADER_PX = HEADER_ROWS * ROW_H so
    // unified cards (which reserve phantom rows above their slots) keep
    // header + slots vertically flush. On narrow viewports we reserve
    // extra rows so the header has room for wrapped text.
    function computeHeaderRows() {
        const w = window.innerWidth || 1200;
        // Reserve just enough rows above the slot area for the
        // header text (kind+edit, time+items+drive, address). Short
        // values keep cards compact — at narrow widths the address
        // line may wrap to two lines, which the third row covers.
        if (w < 700)  return 3;
        return 2;
    }
    let HEADER_ROWS = computeHeaderRows();
    let HEADER_PX = HEADER_ROWS * ROW_H;
    // Time axis: 8 AM through 5 PM = 9 one-hour bins. Equal width per
    // hour so a 1-hour job is the same size everywhere.
    const HOURS = 9;
    // Card / tick positions are % of SCHED_DUR — the time axis is the
    // 1fr column of the .sched-table grid, so it scales with viewport.
    function minToPct(min) {
        if (min <= 0) return 0;
        if (min >= SCHED_DUR) return 100;
        return (min / SCHED_DUR) * 100;
    }

    // Render a time range like "10-12PM" or "11AM-12:30PM". Always shows
    // a single AM/PM at the end (drops the start's suffix even when it
    // differs — feedback explicitly asked for the "10-12PM" shape).
    function fmtRange(startRel, durMin) {
        const startTotal = SCHED_START_MIN + startRel;
        const endTotal = startTotal + durMin;
        const sH = Math.floor(startTotal / 60);
        const sMm = startTotal % 60;
        const eH = Math.floor(endTotal / 60);
        const eMm = endTotal % 60;
        const eAmpm = eH < 12 ? 'AM' : 'PM';
        const sH12 = sH % 12 === 0 ? 12 : sH % 12;
        const eH12 = eH % 12 === 0 ? 12 : eH % 12;
        const sStr = sMm === 0 ? String(sH12) : sH12 + ':' + String(sMm).padStart(2, '0');
        const eStr = eMm === 0 ? String(eH12) : eH12 + ':' + String(eMm).padStart(2, '0');
        return sStr + '-' + eStr + eAmpm;
    }

    // Populate the page-level chip bar with one draggable chip per
    // staff member. Chips are nested in groups so wrapping cascades
    // gracefully on narrow viewports:
    //   Outer  (sched-chips)  → flex-wrap: wrap
    //     Stagers   group     → nowrap (3 chips)
    //     Movers    group     → flex-wrap: wrap
    //       First 4 movers    → nowrap
    //       Last  4 movers    → nowrap
    // So as the viewport tightens, the movers row wraps first, then
    // the last-4-movers wraps to its own row.
    function ensureChipsBar() {
        const bar = document.getElementById('sched-chips');
        if (!bar || bar.dataset.populated === '1') return;

        const makeChip = staff => {
            const isStager = staff.roles.includes('stager') &&
                             !staff.roles.includes('mover');
            const role = isStager ? 'stager' : 'mover';
            const chip = document.createElement('span');
            chip.className = 'sched-chip role-' + role;
            chip.dataset.name = staff.name;
            chip.dataset.role = role;
            chip.draggable = true;
            chip.textContent = staff.name;
            wireEmployeeNameDrag(chip, staff);
            return chip;
        };

        const stagers = ROSTER.filter(s =>
            s.roles.includes('stager') && !s.roles.includes('mover'));
        const movers = ROSTER.filter(s => s.roles.includes('mover'));

        const stagersGrp = document.createElement('div');
        stagersGrp.className = 'sched-chip-group sched-chip-group-stagers';
        stagers.forEach(s => stagersGrp.appendChild(makeChip(s)));

        const moversGrp = document.createElement('div');
        moversGrp.className = 'sched-chip-group sched-chip-group-movers';
        const moversFirst = document.createElement('div');
        moversFirst.className = 'sched-chip-subgroup';
        const moversLast = document.createElement('div');
        moversLast.className = 'sched-chip-subgroup';
        movers.slice(0, 4).forEach(m => moversFirst.appendChild(makeChip(m)));
        movers.slice(4).forEach(m => moversLast.appendChild(makeChip(m)));
        moversGrp.appendChild(moversFirst);
        moversGrp.appendChild(moversLast);

        bar.appendChild(stagersGrp);
        bar.appendChild(moversGrp);
        bar.dataset.populated = '1';
    }

    function renderSchedule(opts) {
        opts = opts || {};
        const grid = document.getElementById('sched-grid');
        const scrollEl = document.getElementById('sched-scroll');
        if (!grid) return;
        const prevScroll = scrollEl ? scrollEl.scrollTop : 0;
        const prevScrollX = scrollEl ? scrollEl.scrollLeft : 0;
        grid.innerHTML = '';

        const startD = new Date(schedAnchor);
        startD.setDate(startD.getDate() - 2);
        const days = 14;

        const titleEl = document.getElementById('sched-title');
        if (titleEl) {
            const endD = new Date(startD);
            endD.setDate(endD.getDate() + days - 1);
            titleEl.textContent = fmt(startD) + ' → ' + fmt(endD) + ', ' + endD.getFullYear();
        }

        const stagers = ROSTER.filter(s => s.roles.includes('stager'));
        const movers  = ROSTER.filter(s => s.roles.includes('mover'));

        for (let i = 0; i < days; i++) {
            const d = new Date(startD);
            d.setDate(startD.getDate() + i);
            const dIso = iso(d);
            const isToday = dIso === iso(today);
            const dow = d.getDay();
            const sec = document.createElement('div');
            sec.className = 'sched-day' +
                (isToday ? ' today' : '') +
                ((dow === 0 || dow === 6) ? ' weekend' : '');
            sec.dataset.date = dIso;

            // Short date label "Apr 24 Fri" — rendered into the
            // axis-corner cell next to the hour ticks.
            const monthShort = d.toLocaleDateString('en-US', { month: 'short' });
            const weekdayShort = d.toLocaleDateString('en-US', { weekday: 'short' });
            const dateLabel = monthShort + ' ' + d.getDate() + ' ' + weekdayShort;

            const cards = cardsForDay(dIso);

            // Per-card meta — every card is "unified" (header + slots in
            // a single self-contained box). Slot count drives lane height.
            const cardMeta = new Map();
            cards.forEach(card => {
                const cardSlots = slotsForCard(card);
                cardMeta.set(card.dataset.sid, {
                    isUnified: true,
                    slotCount: cardSlots.length,
                });
            });

            // Lane assignment — same-start cards stack into separate
            // lanes; different-start cards may share a lane and overlap
            // horizontally where their time ranges intersect (z-stacking
            // keeps them readable, and click-to-focus pulls a covered
            // card to the front).
            const cardLane = new Map();
            const sameStart = new Map();
            cards.forEach(card => {
                const eta = card.dataset.eta || '10:00';
                if (!sameStart.has(eta)) sameStart.set(eta, []);
                sameStart.get(eta).push(card);
            });
            sameStart.forEach(grp => {
                grp.forEach((card, i) => cardLane.set(card.dataset.sid, i));
            });
            // No lane top zone any more — each card's HEADER lives at its
            // own HEADER_ROWS phantoms in the row-aligned area, so columns
            // need no padding-top to reserve space.
            const maxLane = -1;
            const laneHeight = [];
            const laneTop = [];
            const totalHeaderPx = 0;

            // Z-index base — earlier-starting cards default to lower z so
            // a later card sits on top in the overlap region. Click puts
            // a card at zIndex 50 to override.
            const cardZBase = new Map();
            cards.slice().sort((a, b) =>
                timeToOffset(a.dataset.eta || '00:00') -
                timeToOffset(b.dataset.eta || '00:00')
            ).forEach((c, i) => cardZBase.set(c.dataset.sid, 3 + i));

            // Row-aligned layout. For each card (in time order):
            //   1. Resolve its slots — filled → existing employee row or
            //      a fresh employee row; empty → fresh phantom row keyed
            //      to THIS card (sid), so same-start cards each get their
            //      own phantom rows and stack vertically.
            //   2. If any slot needed a fresh row, prepend HEADER_ROWS
            //      phantom info rows BEFORE the new rows so the header
            //      sits directly above the card's first slot.
            //   3. If every slot reuses existing employee rows (e.g. a
            //      Consultation reusing the morning Staging's stager) the
            //      card piggybacks on those rows — they share Y.
            // Non-team roster fills in at the bottom afterwards.
            const rowDefs = [];
            const empIdx = new Map();
            const phantomKey = (sid, role, index) => sid + '|' + role + '|' + index;
            const phantomIdx = new Map();
            const cardLayout = new Map();
            function shiftIndicesFrom(pivot, delta) {
                empIdx.forEach((v, k) => { if (v >= pivot) empIdx.set(k, v + delta); });
                phantomIdx.forEach((v, k) => { if (v >= pivot) phantomIdx.set(k, v + delta); });
                cardLayout.forEach(layout => {
                    layout.slotRows.forEach(s => {
                        if (s.idx >= pivot) s.idx += delta;
                    });
                });
            }

            // Group cards: unassigned (no slots filled) first, assigned
            // (any slot filled) last. Within unassigned, time-sorted
            // cards share a "lane" (one phantom-row block) when their
            // start times are ≥60 min apart, so they overlap horizontally
            // and visually share Y. Same-start cards never share a lane,
            // so they stack vertically.
            const isUnassigned = c => slotsForCard(c).every(s => !s.filled);
            const byStart = (a, b) =>
                timeToOffset(a.dataset.eta || '00:00') -
                timeToOffset(b.dataset.eta || '00:00');
            const unassignedCards = cards.filter(isUnassigned).sort(byStart);
            const assignedCards   = cards.filter(c => !isUnassigned(c)).sort(byStart);

            // Bucket unassigned cards into lanes.
            const unassignedLanes = [];
            unassignedCards.forEach(card => {
                const eta = timeToOffset(card.dataset.eta || '00:00');
                const lane = unassignedLanes.find(L =>
                    L.cards.every(c => Math.abs(
                        timeToOffset(c.dataset.eta || '00:00') - eta) >= 60));
                if (lane) lane.cards.push(card);
                else unassignedLanes.push({ cards: [card] });
            });

            // Allocate one row block per lane: HEADER_ROWS info rows +
            // one phantom-slot row per (role, index) found across the
            // lane's cards.  Cards in the lane reuse those rows, so a
            // 10-12 destage and an 11-1 destage share Y.
            unassignedLanes.forEach(lane => {
                const leadSid = lane.cards[0].dataset.sid;
                const maxByRole = { stager: 0, mover: 0 };
                lane.cards.forEach(c => {
                    slotsForCard(c).forEach(slot => {
                        maxByRole[slot.role] = Math.max(
                            maxByRole[slot.role] || 0, slot.index + 1);
                    });
                });
                for (let h = 0; h < HEADER_ROWS; h++) {
                    rowDefs.push({ kind: 'info', sid: leadSid });
                }
                const protoIdx = {};
                ['stager', 'mover'].forEach(role => {
                    for (let i = 0; i < (maxByRole[role] || 0); i++) {
                        protoIdx[role + ':' + i] = rowDefs.length;
                        rowDefs.push({ kind: 'phantom-slot', sid: leadSid,
                            role, index: i });
                    }
                });
                lane.cards.forEach(card => {
                    const slots = slotsForCard(card);
                    const slotRows = slots.map(slot => ({
                        idx: protoIdx[slot.role + ':' + slot.index],
                        slot,
                    }));
                    cardLayout.set(card.dataset.sid, { slotRows });
                });
            });

            // Now place the assigned cards beneath. Each card's filled
            // slots claim or reuse an employee row; remaining empty
            // slots get fresh phantom rows next to the existing rows.
            assignedCards.forEach(card => {
                const sid = card.dataset.sid;
                const slots = slotsForCard(card);

                const existingPositions = slots
                    .map(slot => slot.filled && empIdx.has(slot.filled)
                        ? empIdx.get(slot.filled) : null)
                    .filter(x => x != null);
                const newSlots = slots.filter(slot =>
                    !(slot.filled && empIdx.has(slot.filled)));

                const slotRows = [];

                if (existingPositions.length === 0) {
                    for (let h = 0; h < HEADER_ROWS; h++) {
                        rowDefs.push({ kind: 'info', sid });
                    }
                    slots.forEach(slot => {
                        if (slot.filled) {
                            const staff = ROSTER.find(r => r.name === slot.filled);
                            if (!staff) return;
                            const idx = rowDefs.length;
                            empIdx.set(slot.filled, idx);
                            rowDefs.push({ kind: 'employee', staff });
                            slotRows.push({ idx, slot });
                        } else {
                            const idx = rowDefs.length;
                            phantomIdx.set(
                                phantomKey(sid, slot.role, slot.index), idx);
                            rowDefs.push({ kind: 'phantom-slot', sid,
                                role: slot.role, index: slot.index });
                            slotRows.push({ idx, slot });
                        }
                    });
                } else if (newSlots.length === 0) {
                    slots.forEach(slot => {
                        slotRows.push({ idx: empIdx.get(slot.filled), slot });
                    });
                } else {
                    const lastExisting = Math.max(...existingPositions);
                    const insertPos = lastExisting + 1;
                    const insertions = newSlots.map(slot => slot.filled
                        ? { kind: 'employee',
                            staff: ROSTER.find(r => r.name === slot.filled) }
                        : { kind: 'phantom-slot', sid,
                            role: slot.role, index: slot.index });
                    rowDefs.splice(insertPos, 0, ...insertions);
                    shiftIndicesFrom(insertPos, insertions.length);
                    let cursor = insertPos;
                    newSlots.forEach(slot => {
                        if (slot.filled) {
                            empIdx.set(slot.filled, cursor);
                        } else {
                            phantomIdx.set(
                                phantomKey(sid, slot.role, slot.index), cursor);
                        }
                        cursor++;
                    });
                    slots.forEach(slot => {
                        if (slot.filled) {
                            slotRows.push({ idx: empIdx.get(slot.filled), slot });
                        } else {
                            slotRows.push({ idx: phantomIdx.get(
                                phantomKey(sid, slot.role, slot.index)), slot });
                        }
                    });
                }
                cardLayout.set(sid, { slotRows });
            });
            // Append non-team roster (anyone not already on a card).
            ROSTER.forEach(s => {
                if (!empIdx.has(s.name)) {
                    empIdx.set(s.name, rowDefs.length);
                    rowDefs.push({ kind: 'employee', staff: s });
                }
            });

            // Build the grid. Track-col width is fixed in pixels (sum of
            // hour widths) so cards can position absolutely with no
            // ambiguity. The whole .sched-day overflows horizontally if
            // the day's content exceeds the viewport.
            const tbl = document.createElement('div');
            tbl.className = 'sched-table';
            tbl.style.setProperty('--row-h', ROW_H + 'px');
            tbl.style.setProperty('--header-h', totalHeaderPx + 'px');

            // Sticky hour row: short date in corner + hour ticks in
            // the axis cell. Stays at the top of the scroll viewport.
            const axisRow = document.createElement('div');
            axisRow.className = 'sched-axis-row';
            const axisCorner = document.createElement('div');
            axisCorner.className = 'sched-axis-corner';
            axisCorner.textContent = dateLabel;
            axisRow.appendChild(axisCorner);
            const axis = document.createElement('div');
            axis.className = 'sched-axis';
            // Visible ticks: 9 AM through 4 PM (skip 8:30 start and
            // 5 PM end edges).
            for (let h = 9; h <= 16; h++) {
                const t = h * 60 - SCHED_START_MIN;
                const tick = document.createElement('div');
                tick.className = 'sched-tick';
                tick.style.left = minToPct(t) + '%';
                const h12 = h % 12 === 0 ? 12 : h % 12;
                const ampm = h < 12 ? 'AM' : 'PM';
                tick.textContent = h12 + ampm;
                axis.appendChild(tick);
            }
            axisRow.appendChild(axis);
            sec.appendChild(axisRow);

            // Body columns.
            const nameCol = document.createElement('div');
            nameCol.className = 'sched-name-col';
            const trackCol = document.createElement('div');
            trackCol.className = 'sched-track-col';
            trackCol.dataset.date = dIso;
            wireJobLaneDrop(trackCol);
            // Click on the empty track-col background → unfocus.
            trackCol.addEventListener('click', e => {
                if (e.target !== trackCol) return;
                if (_focusedSid) focusJobCard(null);
            });

            rowDefs.forEach(row => {
                const nameEl = document.createElement('div');
                const trackEl = document.createElement('div');

                if (row.kind === 'employee') {
                    const isStager = row.staff.roles.includes('stager') &&
                                     !row.staff.roles.includes('mover');
                    const role = isStager ? 'stager' : 'mover';
                    const onTeam = cards.some(c =>
                        slotsForCard(c).some(s => s.filled === row.staff.name));
                    // First column is read-only label; drag source is
                    // the chip row at the top of the day.
                    nameEl.className = 'sched-name role-' + role +
                        (onTeam ? ' team' : '');
                    nameEl.dataset.name = row.staff.name;
                    nameEl.dataset.role = role;
                    nameEl.textContent = row.staff.name;

                    trackEl.className = 'sched-track role-' + role;
                    trackEl.dataset.name = row.staff.name;
                    trackEl.dataset.role = role;
                    trackEl.dataset.date = dIso;
                    const shift = document.createElement('div');
                    shift.className = 'sched-shift-bar';
                    const sh = isStager ? SHIFT_STAGER : SHIFT_MOVER;
                    shift.style.left  = minToPct(sh.start) + '%';
                    shift.style.width = (minToPct(sh.end) - minToPct(sh.start)) + '%';
                    trackEl.appendChild(shift);

                    // Drive / load / unload busy markers from segments
                    // OUTSIDE the onsite window. We tag each marker
                    // with its associated card sid + which side of the
                    // card it sits on + its order from the card edge.
                    // A post-render pass uses these tags to switch to
                    // a fixed-50 px adjacent layout when the card
                    // hits its min-width clamp.
                    cards.forEach(card => {
                        if (!isAssignedTo(card, row.staff.name, role)) return;
                        const cardEta = timeToOffset(card.dataset.eta || '10:00');
                        const cardEnd = cardEta + cardDurMin(card);
                        const allSegs = buildSegments(card, role).filter(s =>
                            s.kind !== 'stage' && s.kind !== 'consult' &&
                            s.kind !== 'design');
                        // Skip segments that fall inside the card range
                        // (those are visually covered by the card slot
                        // anyway).
                        const before = allSegs
                            .filter(s => s.start + s.dur <= cardEta)
                            .sort((a, b) => b.start - a.start);
                        const after  = allSegs
                            .filter(s => s.start >= cardEnd)
                            .sort((a, b) => a.start - b.start);
                        const tag = (seg, side, order) => {
                            const c = clipSegment(seg.start, seg.start + seg.dur);
                            if (c.s1 <= c.s0) return;
                            const block = document.createElement('div');
                            block.className = 'sched-busy kind-' + seg.kind +
                                (c.clipped ? ' clipped' : '');
                            const x0 = minToPct(c.s0);
                            const x1 = minToPct(c.s1);
                            block.style.left  = x0 + '%';
                            block.style.width = (x1 - x0) + '%';
                            block.dataset.sid   = card.dataset.sid;
                            block.dataset.side  = side;
                            block.dataset.order = String(order);
                            block.dataset.kind  = seg.kind;
                            block.title = seg.label + ' · ' + (seg.sub || '') +
                                ' · ' + fmtAbs(seg.start) + '–' + fmtAbs(seg.start + seg.dur) +
                                (c.clipped ? ' (outside shift)' : '');
                            block.textContent = seg.label;
                            trackEl.appendChild(block);
                        };
                        before.forEach((s, i) => tag(s, 'before', i));
                        after.forEach((s, i) => tag(s, 'after',  i));
                    });
                } else {
                    // Phantom row: blank in column, blank track. Job card
                    // overlay will fill the corresponding row inside it.
                    nameEl.className = 'sched-name phantom';
                    trackEl.className = 'sched-track phantom';
                }

                nameCol.appendChild(nameEl);
                trackCol.appendChild(trackEl);
            });

            // Job overlays — header element above row 0, slots element at
            // the team's row offsets. Two siblings per card so the same
            // employee row can be reused across multiple jobs without
            // header phantoms wasting vertical space.
            cards.forEach(card => {
                const lane = cardLane.get(card.dataset.sid) || 0;
                const zb   = cardZBase.get(card.dataset.sid) || 3;
                const meta = cardMeta.get(card.dataset.sid);
                appendJobToTrack(card, dIso, cardLayout, trackCol,
                    lane, zb, totalHeaderPx, laneTop[lane], meta);
            });
            // After all cards added, mark which ones are "covering" so
            // CSS can dim them and let the covered card show through.
            recomputeOverlaps(sec);

            tbl.appendChild(nameCol);
            tbl.appendChild(trackCol);
            sec.appendChild(tbl);
            grid.appendChild(sec);
        }

        // Auto-size each card header to its content height. Per-day:
        //   1. Measure each header's natural height (scrollHeight only
        //      works once the section is in the live document).
        //   2. If any header would overflow above its reserved phantom
        //      rows (naturalH > slotTop), add the worst overflow as
        //      padding-top to the day's nameCol + trackCol, then shift
        //      every absolutely-positioned card element (header + slots)
        //      down by the same amount. This pushes the body just far
        //      enough that the tallest header still fits below the
        //      sticky hour row.
        //   3. Bottom-anchor each header at its (shifted) slot top.
        grid.querySelectorAll('.sched-day').forEach(sec => {
            const nameCol  = sec.querySelector('.sched-name-col');
            const trackCol = sec.querySelector('.sched-track-col');
            const headers  = Array.from(sec.querySelectorAll('.sched-job-header'));
            const slotsAll = Array.from(sec.querySelectorAll('.sched-job-slots'));
            if (!headers.length) return;
            let dayOverflow = 0;
            const info = headers.map(h => {
                const slotTop = parseFloat(h.dataset.slotTopPx || '0') || 0;
                const naturalH = h.scrollHeight || HEADER_PX;
                if (naturalH > slotTop) {
                    dayOverflow = Math.max(dayOverflow, naturalH - slotTop);
                }
                return { h, slotTop, naturalH };
            });
            if (dayOverflow > 0) {
                if (nameCol)  nameCol.style.paddingTop  = dayOverflow + 'px';
                if (trackCol) trackCol.style.paddingTop = dayOverflow + 'px';
                slotsAll.forEach(s => {
                    const t = parseFloat(s.style.top) || 0;
                    s.style.top = (t + dayOverflow) + 'px';
                });
            }
            info.forEach(({ h, slotTop, naturalH }) => {
                h.style.height = naturalH + 'px';
                h.style.top    = (slotTop + dayOverflow - naturalH) + 'px';
            });

            // When a card is clamped to its min-width (= time-natural
            // width is below the floor), position its drive/load
            // markers as fixed-50 px tiles flush against the card's
            // visual edges, with "D" / "L" abbreviations. Otherwise
            // keep the time-proportional placement.
            const COMPACT_W = 30;
            const trackWidthPx = trackCol ? trackCol.clientWidth : 0;
            sec.querySelectorAll('.sched-job-header').forEach(headerEl => {
                const sid = headerEl.dataset.sid;
                if (!sid) return;
                const naturalPx = (parseFloat(headerEl.style.width) / 100) * trackWidthPx;
                const actualPx  = headerEl.offsetWidth;
                const isCompact = actualPx > naturalPx + 1;
                if (!isCompact) return;
                const cardLeftPx  = headerEl.offsetLeft;
                const cardRightPx = cardLeftPx + actualPx;
                trackCol.querySelectorAll(
                    '.sched-busy[data-sid="' + sid + '"]'
                ).forEach(b => {
                    const side  = b.dataset.side;
                    const order = parseInt(b.dataset.order, 10) || 0;
                    const x = (side === 'before')
                        ? cardLeftPx - (order + 1) * COMPACT_W
                        : cardRightPx + order * COMPACT_W;
                    b.style.left  = x + 'px';
                    b.style.width = COMPACT_W + 'px';
                    b.textContent = b.dataset.kind === 'drive' ? 'D' : 'L';
                });
            });
        });

        // Scroll today into view on first render / Today click; otherwise
        // restore where the user was (so drag-drop doesn't yank the page).
        if (scrollEl) {
            if (opts.scrollToToday) {
                const todaySec = grid.querySelector('.sched-day.today');
                if (todaySec) scrollEl.scrollTop = todaySec.offsetTop - 4;
                else scrollEl.scrollTop = prevScroll;
            } else {
                scrollEl.scrollTop = prevScroll;
            }
            scrollEl.scrollLeft = prevScrollX;
        }
    }

    // Build & append a job's two elements (header + slots) directly to
    // the day's track-col. Two siblings — not one wrapper — so the
    // header can sit in the padding-top zone (top:0..HEADER_PX) while
    // the slots anchor to the team's row offsets. The same employee row
    // is reused across every job they appear in. lane/zBase let same-
    // start cards stack vertically, and overlapping headers resolve via
    // z-index + .is-covering opacity.
    function appendJobToTrack(card, dIso, cardLayout, trackCol,
                              lane, zBase, totalHeaderPx, laneTopPx, meta) {
        const layout = cardLayout.get(card.dataset.sid);
        if (!layout || !layout.slotRows.length) return;
        const kind = card.dataset.kind;
        const eta = card.dataset.eta || '10:00';
        const etaMin = timeToOffset(eta);
        const items = parseInt(card.dataset.items || '0', 10);
        const drv = parseInt(card.dataset.driving || '0', 10) || 30;

        // Onsite duration → card width. Card covers the property-side
        // work only; drive segments appear OUTSIDE the card on either
        // side (left = drive to property, right = drive back / to
        // warehouse), so before/after drive bars look symmetric.
        let dur;
        if (kind === 'Staging')           dur = STAGE_ONSITE_STAGER;
        else if (kind === 'Destage')      dur = Math.max(60, items * 2);
        else if (kind === 'Consultation') dur = CONSULT_ONSITE;
        else if (kind === 'Design')       dur = DESIGN_ONSITE;
        else                              dur = 90;

        const c = clipSegment(etaMin, etaMin + dur);
        const leftPct  = minToPct(c.s0);
        const widthPct = minToPct(c.s1) - leftPct;

        // Slot rows are row-aligned with the employee tracks below; the
        // card's header sits HEADER_ROWS rows above the card's first
        // slot row.
        const slotIdxs = layout.slotRows.map(s => s.idx);
        const firstSlot = slotIdxs.length ? Math.min(...slotIdxs) : 0;
        const lastSlot  = slotIdxs.length ? Math.max(...slotIdxs) : 0;
        const rowsCovered = slotIdxs.length ? (lastSlot - firstSlot + 1) : 0;

        const itemsLbl = items + ' item' + (items !== 1 ? 's' : '');
        const driveLbl = drv + 'm drive';
        const timeRange = fmtRange(c.s0, c.s1 - c.s0);
        const tooltip = kind + ' ' + timeRange + ' · ' + (card.dataset.addr || '') +
            ' · ' + itemsLbl + ' · ' + driveLbl;

        // Header element — anchored HEADER_ROWS rows above the card's
        // first slot row, so it sits directly above the team's slots.
        const isFocused = (_focusedSid === card.dataset.sid);
        const headerTopPx = (firstSlot - HEADER_ROWS) * ROW_H;
        const header = document.createElement('div');
        header.className = 'sched-job-header kind-' + kind.toLowerCase() +
            (isFocused ? ' focused' : '');
        header.draggable = true;
        header.dataset.sid = card.dataset.sid;
        header.dataset.date = dIso;
        header.dataset.zBase = String(zBase);
        // Initial position — top will be re-anchored after the header
        // measures its actual content height (so each card auto-sizes
        // to its content rather than all sharing HEADER_PX).
        header.style.top    = headerTopPx + 'px';
        header.style.left   = leftPct + '%';
        header.style.width  = widthPct + '%';
        header.style.zIndex = isFocused ? 50 : zBase;
        header.title = tooltip;
        // Edit button — pen icon, opens the universal staging modal.
        // Design cards use the parent staging's sid (stripped of '_dp').
        const sidForEdit = (card.dataset.sid || '').replace(/_dp$/, '');
        const editBtn = sidForEdit
            ? '<button type="button" class="sched-edit-btn" title="Edit staging" '
              + 'data-sid="' + sidForEdit + '">'
              + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              + 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
              + '<path d="M12 20h9"/>'
              + '<path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>'
              + '</svg></button>'
            : '';
        // Mobile shorthand: "CONSULTATION" → "CONSULT" so it fits on
        // one line of a narrow card. CSS handles only one of the two
        // labels via a media query that toggles their display.
        const kindLabel =
            '<span class="kind nowrap kind-long">' + kind + '</span>' +
            (kind === 'Consultation'
                ? '<span class="kind nowrap kind-short">Consult</span>'
                : '');
        header.innerHTML =
            '<div class="line first">' +
                kindLabel +
                editBtn +
                '<span class="spacer"></span>' +
            '</div>' +
            '<div class="line addr">' + escapeHtml(card.dataset.addr || '—') + '</div>' +
            '<div class="line meta">' +
                '<span class="time nowrap">' + timeRange + '</span>' +
                '<span class="item-drive">' +
                    '<span class="item nowrap">' + itemsLbl + '</span>' +
                    '<span class="drive nowrap">' + driveLbl + '</span>' +
                '</span>' +
            '</div>';
        wireJobHandleDrag(header, header);
        wireJobAreaEmployeeDrop(header, card);
        // Click toggles focus — clicking the focused card again unfocuses.
        header.addEventListener('click', e => {
            // ✎ edit button: stop the focus toggle and open the modal.
            const editEl = e.target.closest('.sched-edit-btn');
            if (editEl) {
                e.stopPropagation();
                if (window.StagingEditModal) {
                    StagingEditModal.open(editEl.dataset.sid);
                }
                return;
            }
            focusJobCard(_focusedSid === card.dataset.sid
                ? null : card.dataset.sid);
        });
        trackCol.appendChild(header);

        // Slots element — anchored to the card's slot rows in the
        // row-aligned area. Height covers from firstSlot through
        // lastSlot inclusive (gaps fill if non-contiguous).
        const slots = document.createElement('div');
        slots.className = 'sched-job-slots kind-' + kind.toLowerCase() +
            (isFocused ? ' focused' : '');
        slots.dataset.sid = card.dataset.sid;
        slots.dataset.date = dIso;
        slots.dataset.zBase = String(zBase);
        slots.style.top    = (firstSlot * ROW_H) + 'px';
        slots.style.height = (rowsCovered * ROW_H) + 'px';
        slots.style.left   = leftPct + '%';
        slots.style.width  = widthPct + '%';
        slots.style.zIndex = isFocused ? 50 : zBase;
        slots.title = tooltip;
        // Drop an employee on the slots-area background (between/over
        // gap rows) follows the same rules as dropping on the header.
        wireJobAreaEmployeeDrop(slots, card);
        // Click on the slots area too → toggle focus (so users can grab
        // either piece of a card to focus / unfocus it).
        slots.addEventListener('click', e => {
            // Don't trigger focus when the user clicked a draggable child
            // (the staff pill).
            if (e.target.closest('[draggable="true"]')) return;
            focusJobCard(_focusedSid === card.dataset.sid
                ? null : card.dataset.sid);
        });
        // Iterator differs by mode: unified cards render slots in their
        // natural order (no row indices); split cards render rows from
        // firstRow..lastRow with empty gap-rows for any missing.
        const renderSlot = slot => {
            const slotEl = document.createElement('div');
            slotEl.className = 'sched-job-slot role-' + slot.role +
                (slot.filled ? '' : ' empty');
            slotEl.dataset.sid = card.dataset.sid;
            slotEl.dataset.role = slot.role;
            slotEl.dataset.index = String(slot.index);
            slotEl.dataset.date = dIso;
            const badge = '<span class="badge">' +
                slot.role[0].toUpperCase() + '</span>';
            if (slot.filled) {
                const who = document.createElement('span');
                who.className = 'who';
                who.textContent = slot.filled;
                who.draggable = true;
                wirePillDrag(who, slotEl);
                const remove = document.createElement('button');
                remove.type = 'button';
                remove.className = 'slot-remove';
                remove.textContent = '×';
                remove.title = 'Remove ' + slot.filled;
                remove.addEventListener('click', e => {
                    e.stopPropagation();
                    setSlotAssign(dIso, card.dataset.sid,
                        slot.role, slot.index, null);
                    renderSchedule();
                });
                slotEl.innerHTML = badge;
                slotEl.appendChild(who);
                slotEl.appendChild(remove);
            } else {
                slotEl.innerHTML = badge +
                    '<span class="who">drop staff</span>';
            }
            wireSlotEmployeeDrop(slotEl);
            return slotEl;
        };
        // Render slot rows in row-index order so they line up with
        // the underlying employee tracks. Gap rows fill any holes when
        // the same employee is shared across multiple cards and the
        // current card's slot indices are non-contiguous.
        const slotMap = new Map(layout.slotRows.map(s => [s.idx, s.slot]));
        for (let r = firstSlot; r <= lastSlot; r++) {
            const slot = slotMap.get(r);
            if (!slot) {
                const gapEl = document.createElement('div');
                gapEl.className = 'sched-job-slot empty gap';
                gapEl.style.background = 'transparent';
                gapEl.style.borderTop = '0';
                slots.appendChild(gapEl);
                continue;
            }
            slots.appendChild(renderSlot(slot));
        }
        trackCol.appendChild(slots);

        // Stash the slot top in the header so a post-render pass can
        // bottom-anchor the header to its slot row once the day section
        // is in the document (scrollHeight is unreliable on detached
        // subtrees).
        header.dataset.slotTopPx = String(firstSlot * ROW_H);
    }

    // Drag handle at the top of a job card → reschedule (move horizontally
    // or to another day). dragend always clears the live-time indicator
    // (drop fires before dragend; if the drop succeeded the re-render
    // wipes everything anyway).
    function wireJobHandleDrag(handleEl, jobEl) {
        handleEl.addEventListener('dragstart', e => {
            e.stopPropagation();
            jobEl.classList.add('dragging');
            _schedDragPayload = {
                type: 'job',
                sid: jobEl.dataset.sid,
                date: jobEl.dataset.date,
            };
            e.dataTransfer.effectAllowed = 'move';
            try { e.dataTransfer.setData('text/plain', JSON.stringify(_schedDragPayload)); }
            catch(_) {}
        });
        handleEl.addEventListener('dragend', () => {
            jobEl.classList.remove('dragging');
            _schedDragPayload = null;
            hideLiveTime();
        });
    }

    // Compute the eta + percentage offset from a track-col + cursor X.
    // Snaps to the nearest 30-min boundary. Returns the snapped left-%
    // so the live indicator aligns with the snapped time on the fluid
    // axis (which scales with the viewport).
    function etaFromLaneX(laneEl, clientX) {
        const rect = laneEl.getBoundingClientRect();
        const x = Math.max(0, Math.min(rect.width, clientX - rect.left));
        const min = rect.width > 0 ? (x / rect.width) * SCHED_DUR : 0;
        const minOff = Math.max(0, Math.min(SCHED_DUR, Math.round(min / 30) * 30));
        const total = SCHED_START_MIN + minOff;
        const h = Math.floor(total / 60);
        const mm = total % 60;
        return {
            pct: minToPct(minOff),
            minOff,
            eta: String(h).padStart(2, '0') + ':' + String(mm).padStart(2, '0'),
        };
    }

    // Show / move the live-time badge on the day's axis at the given %.
    function showLiveTime(laneEl, pct, eta) {
        const tbl = laneEl.parentElement;
        const axis = tbl ? tbl.querySelector('.sched-axis') : null;
        if (!axis) return;
        let ind = axis.querySelector('.sched-live-time');
        if (!ind) {
            ind = document.createElement('div');
            ind.className = 'sched-live-time';
            axis.appendChild(ind);
        }
        ind.style.left = pct + '%';
        ind.textContent = eta;
        document.querySelectorAll('.sched-live-time').forEach(el => {
            if (el !== ind) el.remove();
        });
    }
    function hideLiveTime() {
        document.querySelectorAll('.sched-live-time').forEach(el => el.remove());
    }

    // For each card-header in the day, set .is-covering when there's any
    // OTHER header beneath it (lower z-index) whose rectangle overlaps.
    // Cards in different lanes (different y range) won't intersect, so
    // same-start cards never trigger this — good, those got separated
    // by lane assignment instead.
    function recomputeOverlaps(dayEl) {
        const headers = Array.from(dayEl.querySelectorAll('.sched-job-header'));
        const rects = headers.map(h => ({
            el: h,
            z: parseInt(h.style.zIndex, 10) || 3,
            l: parseFloat(h.style.left) || 0,
            r: (parseFloat(h.style.left) || 0) + (parseFloat(h.style.width) || 0),
            t: parseFloat(h.style.top) || 0,
            b: (parseFloat(h.style.top) || 0) + (parseFloat(h.style.height) || 0),
        }));
        rects.forEach(a => {
            const isOver = rects.some(b => {
                if (b === a) return false;
                if (b.z >= a.z) return false; // b not beneath a
                return (b.r > a.l) && (b.l < a.r) &&
                       (b.b > a.t) && (b.t < a.b);
            });
            a.el.classList.toggle('is-covering', isOver);
        });
    }

    // Click a card → it becomes the topmost (z-index 50) and applies
    // .focused styling. Re-runs overlap detection so the new arrangement
    // shows the right cards as "covering" (semi-transparent).
    function focusJobCard(sid) {
        _focusedSid = sid;
        document.querySelectorAll('.sched-job-header, .sched-job-slots').forEach(el => {
            const isThis = el.dataset.sid === sid;
            el.classList.toggle('focused', isThis);
            const zb = parseInt(el.dataset.zBase, 10) || 3;
            el.style.zIndex = isThis ? 50 : zb;
        });
        document.querySelectorAll('.sched-day').forEach(day => recomputeOverlaps(day));
    }

    // Drop an employee onto a card's HEADER or non-slot SLOTS area.
    //   - First empty slot of a matching role → fill it.
    //   - Otherwise extend the role array when the card accepts that
    //     role: stager → Staging/Consultation/Design; mover → Staging/
    //     Destage. The new slot stays until removed.
    //   - Otherwise no-op (e.g. dropping a stager on a Destage card).
    function extendableRoleForKind(role, kind) {
        if (role === 'mover')  return kind === 'Staging' || kind === 'Destage';
        if (role === 'stager') return kind === 'Staging' ||
                                      kind === 'Consultation' ||
                                      kind === 'Design';
        return false;
    }
    function wireJobAreaEmployeeDrop(areaEl, card) {
        areaEl.addEventListener('dragover', e => {
            const p = _schedDragPayload;
            if (!p || p.type !== 'employee') return;
            // Only react if the cursor is on the area's own background
            // (or the header text), not on a child slot — those have
            // their own drop handler.
            if (e.target.closest('.sched-job-slot')) return;
            const kind = card.dataset.kind;
            const roles = p.roles || [];
            const empties = unfilledSlots(card)
                .filter(s => roles.includes(s.role));
            const canExtend = roles.some(r => extendableRoleForKind(r, kind));
            if (!empties.length && !canExtend) return;
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'copy';
            areaEl.classList.add('drop-over');
        });
        areaEl.addEventListener('dragleave', e => {
            if (e.relatedTarget && areaEl.contains(e.relatedTarget)) return;
            areaEl.classList.remove('drop-over');
        });
        areaEl.addEventListener('drop', e => {
            areaEl.classList.remove('drop-over');
            const p = _schedDragPayload;
            if (!p || p.type !== 'employee') return;
            if (e.target.closest('.sched-job-slot')) return;
            const kind = card.dataset.kind;
            const roles = p.roles || [];
            const dIso = card.dataset.date;
            const sid = card.dataset.sid;
            // Prefer filling an empty matching slot.
            const target = unfilledSlots(card)
                .find(s => roles.includes(s.role));
            if (target) {
                e.preventDefault();
                e.stopPropagation();
                setSlotAssign(dIso, sid, target.role, target.index, p.name);
                renderSchedule();
                return;
            }
            // No empty slot — extend an array. Pick a role the employee
            // can perform that the card accepts.
            const extRole = roles.find(r => extendableRoleForKind(r, kind));
            if (!extRole) return;
            e.preventDefault();
            e.stopPropagation();
            const m = getDayAssign(dIso);
            const a = m[sid] || {};
            const arr = (extRole === 'stager') ? readStagers(a) : readMovers(a);
            setSlotAssign(dIso, sid, extRole, arr.length, p.name);
            renderSchedule();
        });
    }

    // Drop an employee name onto an empty slot row → assign that exact slot.
    function wireSlotEmployeeDrop(slotEl) {
        slotEl.addEventListener('dragover', e => {
            const p = _schedDragPayload;
            if (!p || p.type !== 'employee') return;
            // Role match required.
            if (!(p.roles || []).includes(slotEl.dataset.role)) return;
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'copy';
            slotEl.classList.add('drop-over');
        });
        slotEl.addEventListener('dragleave', () => slotEl.classList.remove('drop-over'));
        slotEl.addEventListener('drop', e => {
            slotEl.classList.remove('drop-over');
            const p = _schedDragPayload;
            if (!p || p.type !== 'employee') return;
            if (!(p.roles || []).includes(slotEl.dataset.role)) return;
            e.preventDefault();
            e.stopPropagation();
            setSlotAssign(slotEl.dataset.date, slotEl.dataset.sid,
                slotEl.dataset.role,
                parseInt(slotEl.dataset.index || '0', 10),
                p.name);
            renderSchedule();
        });
    }

    // Drag a filled slot's name out of the card → remove that staff. The
    // pill (`.who` span) is the drag source so dragging it past the card
    // edge yields dropEffect === 'none', which we treat as removal.
    function wirePillDrag(whoEl, slotEl) {
        whoEl.addEventListener('dragstart', e => {
            e.stopPropagation();
            slotEl.classList.add('removing');
            _schedDragPayload = {
                type: 'pill',
                sid: slotEl.dataset.sid,
                role: slotEl.dataset.role,
                index: parseInt(slotEl.dataset.index || '0', 10),
                date: slotEl.dataset.date,
            };
            e.dataTransfer.effectAllowed = 'move';
            try { e.dataTransfer.setData('text/plain', JSON.stringify(_schedDragPayload)); }
            catch(_) {}
        });
        whoEl.addEventListener('dragend', e => {
            slotEl.classList.remove('removing');
            const p = _schedDragPayload;
            _schedDragPayload = null;
            if (!p || p.type !== 'pill') return;
            if (e.dataTransfer.dropEffect === 'none') {
                setSlotAssign(p.date, p.sid, p.role, p.index, null);
                renderSchedule();
            }
        });
    }

    // Employee first-name draggable. Drag onto a job card → assign.
    function wireEmployeeNameDrag(nameEl, staff) {
        nameEl.addEventListener('dragstart', e => {
            _schedDragPayload = { type: 'employee', name: staff.name,
                                  roles: staff.roles };
            e.dataTransfer.effectAllowed = 'copy';
            try { e.dataTransfer.setData('text/plain', JSON.stringify(_schedDragPayload)); }
            catch(_) {}
        });
        nameEl.addEventListener('dragend', () => { _schedDragPayload = null; });
    }

    // Jobs lane accepts a job-card drop → reschedule to the dropped X.
    function wireJobLaneDrop(laneEl) {
        laneEl.addEventListener('dragover', e => {
            if (!_schedDragPayload || _schedDragPayload.type !== 'job') return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            laneEl.classList.add('drop-over');
            // Live-time indicator follows the cursor as the user moves
            // over this day's lane — no commit until drop.
            const t = etaFromLaneX(laneEl, e.clientX);
            showLiveTime(laneEl, t.pct, t.eta);
        });
        laneEl.addEventListener('dragleave', e => {
            // Only clear when leaving the lane itself, not a child.
            if (e.relatedTarget && laneEl.contains(e.relatedTarget)) return;
            laneEl.classList.remove('drop-over');
        });
        laneEl.addEventListener('drop', e => {
            laneEl.classList.remove('drop-over');
            const p = _schedDragPayload;
            if (!p || p.type !== 'job') return;
            e.preventDefault();
            hideLiveTime();
            const t = etaFromLaneX(laneEl, e.clientX);
            const card = document.querySelector('.cal-card[data-sid="' + p.sid + '"]');
            if (card) {
                card.dataset.eta = t.eta;
                if (card.dataset.slot) card.dataset.slot = '';
            }
            const newDate = laneEl.dataset.date;
            if (card && newDate && card.dataset.date !== newDate) {
                card.dataset.date = newDate;
            }
            renderSchedule();
        });
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
        toggleKind,
        openDay,
        daySuggest,
        dayClearAll,
        schedToday,
        schedShift,
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

        refreshKindButtons();
        // Pull DB-derived assignments into localStorage before anything
        // renders — schedule + day-detail both read from tb_assign.
        seedAssignmentsFromDefaults();
        setView(state.view);

        // Calendar scroll → title sync. Throttled to one rAF so dragging
        // scrolls feels instant without firing the layout read 60×/sec.
        let titleScheduled = false;
        document.addEventListener('scroll', e => {
            const t = e.target;
            if (!t || !t.classList || !t.classList.contains('cal-view-scroll')) return;
            if (titleScheduled) return;
            titleScheduled = true;
            requestAnimationFrame(() => {
                titleScheduled = false;
                updateTitleFromScroll();
            });
        }, true);
        // Re-render schedule on resize so HEADER_ROWS / column widths
        // adjust to the new viewport — debounced so a window-drag
        // doesn't re-render on every mouse-move.
        let _resizeTimer = null;
        window.addEventListener('resize', () => {
            sizeWeeks();
            updateTitleFromScroll();
            HEADER_ROWS = computeHeaderRows();
            HEADER_PX = HEADER_ROWS * ROW_H;
            if (state.view === 'schedule') {
                clearTimeout(_resizeTimer);
                _resizeTimer = setTimeout(() => renderSchedule(), 120);
            }
        });
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


# -------------------- portal staging modal --------------------
# Field allowlist for the universal Staging edit modal in
# static/staging_edit_modal.js. Anything not in this set is rejected on
# save. Scheduling time fields (Staging_Mover_*_Time, etc.) and Zoho-only
# workflow triggers (Update_*, Email_Customer_to_*, Refresh, etc.) are
# deliberately excluded — they belong to the Schedule view or to dedicated
# action endpoints.
_STAGING_EDITABLE_FIELDS = frozenset({
    # General
    "Staging_Status", "Staging_Furniture_Quality", "Staging_Type",
    "Staging_Complexity", "Is_Showcase",
    "Staging_Address", "Property_Type", "Occupancy_Type",
    "Staging_Date", "Staging_ETA", "Staging_Date_Flexible", "Staging_Term",
    "Destaging_Date", "Destaging_ETA", "Destaging_Date_Flexible",
    "Consultation_Type", "Consultation_Date_and_Time", "Consultation_Stager1",
    "Stager", "Staging_Movers", "Destaging_Movers", "Furniture_Locations",
    # Customer
    "Customer_First_Name", "Customer_Last_Name", "Customer_Email",
    "Customer_Phone", "Customer_Attributes", "Customer_Notes",
    # Moving
    "Total_Item_Number", "Driving_Time", "Dock",
    "Person_To_Provide_Access_for_Staging", "Lockbox_Code_for_Staging",
    "Elevator_Start_Time", "Elevator_Finish_Time", "Staging_Moving_Instructions",
    "Person_To_Provide_Access_for_Destaging", "Lockbox_Code_for_Destaging",
    "Destaging_Moving_Instructions",
    # Design
    "General_Notes", "Consultation_Instructions", "Design_Notes",
    "Staging_Feedback", "Lock_Design", "Show_Design_To_Customer",
    "Check_Basement_Furniture_Size_Date",
    "Staging_Furniture_Design_Finish_Date",
    "Staging_Accessories_Packing_Finish_Date",
    # Payment
    "Total_Staging_Fee", "Initial_Staging_Fee", "Photography_Fee",
    "Moving_Fee", "Monthly_Extension_Fee", "Deposit_Amount",
    "Security_Deposit", "Pay_by_Cash", "Invoice_Sent_Date",
    # Listing
    "MLS", "Listing_Price",
    "Before_Picture_Upload_Date", "After_Picture_Upload_Date",
    # Notify
    "Staging_Item_List", "Seller_To_Do_List", "WhatsApp_Group_Created_Date",
    "Consultation_Confirmation_Email_Sent_Date", "Next_Steps_Email_Sent_Date",
    "Extension_Email_Sent_Date", "Destaging_Confirmation_Email_Sent_Date",
    "Staging_Completion_Confirmation_Sent_Date",
    "Destaging_Completion_Confirmation_Sent_Date",
    "Staging_Review_Request_Sent_Date", "Destaging_Review_Request_Sent_Date",
})

# Columns stored as JSON arrays of {display_value, ID} objects.
_STAGING_PEOPLE_FIELDS = frozenset({
    "Stager", "Staging_Movers", "Destaging_Movers", "Consultation_Stager1",
})
# Columns stored as JSON {display_value, ID} (single).
_STAGING_LINK_FIELDS = frozenset({"Staging_Address", "Quote", "Customer_CRM"})
# Columns stored as JSON arrays of strings (multi-select picklist).
_STAGING_TAG_FIELDS = frozenset({"Customer_Attributes"})


def _serialize_staging_field(key: str, value):
    """Convert a JSON value from the modal into the textual form Zoho writes
    to the local SQLite snapshot. Symmetric with the parsers used by the
    iOS/Android API layer."""
    if value is None:
        return ""
    if key in _STAGING_PEOPLE_FIELDS:
        if not isinstance(value, list):
            return ""
        arr = [_person_json_obj(name) for name in value if name]
        return json.dumps(arr) if arr else ""
    if key in _STAGING_TAG_FIELDS:
        if not isinstance(value, list):
            return ""
        return json.dumps(list(value)) if value else ""
    if key in _STAGING_LINK_FIELDS:
        # Address is editable; store only display_value (no ID lookup
        # available locally). Empty string clears it.
        text = str(value).strip()
        if not text:
            return ""
        return json.dumps({"display_value": text})
    if key == "Pay_by_Cash":
        # Stored as "true"/"false" strings in Zoho.
        if isinstance(value, bool):
            return "true" if value else "false"
        s = str(value).strip().lower()
        return "true" if s in ("true", "1", "yes") else "false"
    return "" if value == "" else str(value)


def _staging_modal_payload(row) -> dict:
    """Shape returned by GET /portal/staging/<id>.

    Splits the row into context (header strip), values (per-field current
    values decoded into JS-friendly form), and roster (for the people
    picker). The schema lives client-side in static/staging_edit_modal.js;
    this function only needs to surface the raw values + roster.
    """
    def col(name):
        try:
            return row[name]
        except Exception:
            return None

    values = {}
    for key in _STAGING_EDITABLE_FIELDS:
        raw = col(key) or ""
        if key in _STAGING_PEOPLE_FIELDS:
            people = _parse_people(raw)
            values[key] = [_display_name(p) for p in people]
        elif key in _STAGING_TAG_FIELDS:
            try:
                arr = json.loads(raw) if raw else []
                values[key] = arr if isinstance(arr, list) else []
            except Exception:
                values[key] = []
        elif key == "Staging_Address":
            values[key] = _parse_link(raw) or ""
        else:
            values[key] = raw or ""

    # Read-only display fields (rendered as 'readonly' / 'readonly-link' in
    # the modal — never sent back on save).
    for key in ("Staging_Display_Name", "Total_Amount", "Paid_Amount",
                "Owing_Amount", "HST", "Total_Extension_Fee", "Days_On_Market",
                "Pictures_Folder", "Design_Items_Matched_Date",
                "Consultation_Notes_Complete_Time", "Customer_Acknowledged_Time"):
        values[key] = col(key) or ""
    values["Quote"] = _parse_link(col("Quote") or "") or ""
    values["Customer_CRM"] = _parse_link(col("Customer_CRM") or "") or ""

    address = _parse_link(col("Staging_Address") or "") or col("Staging_Display_Name") or ""
    date_str = ""
    d = _parse_mdy(col("Staging_Date") or "")
    if d:
        date_str = d.strftime("%a %b %-d")
    eta = _fmt_time_short(col("Staging_ETA") or "")
    stagers = _parse_people(col("Stager") or "")
    movers = _parse_people(col("Staging_Movers") or "")
    team_bits = []
    if stagers:
        team_bits.append(", ".join(_display_name(p) for p in stagers))
    if movers:
        team_bits.append("· " + ", ".join(_display_name(p) for p in movers))
    context = {
        "address": address,
        "staging_date": date_str,
        "staging_eta": eta,
        "team": " ".join(team_bits),
        "status": col("Staging_Status") or "",
    }

    return {
        "id": col("ID"),
        "context": context,
        "values": values,
        "roster": _STAFF_ROSTER,
    }


# -------------------- routes --------------------

def register(rt):

    @rt("/")
    @rt("/staging_task_board")  # legacy — kept so existing bookmarks / links work
    def task_board(request: Request):
        # Staff-only ops home. Unauth users bounce to /signin.
        # Use tools.user_db (data/customers.db) — same DB the Google OAuth
        # + email signin handlers write sessions to. Reading from
        # employees_db.py here would miss those sessions and cause a
        # /signin <-> / redirect loop.
        from tools.user_db import get_user_by_session
        token = request.cookies.get("astra_session")
        user = get_user_by_session(token) if token else None
        if not user:
            return RedirectResponse("/signin", status_code=302)
        rows = _fetch_all_stagings()
        employees = _fetch_employees()
        roster = _fetch_employee_roster()
        corpus = _build_autocomplete_corpus(rows, employees)
        grouped = _group_by_date(rows)
        date_min, date_max = _date_bounds(rows)

        table_view = _build_table(grouped)
        cal_toolbar, cal_scroll, cal_source = _build_calendar_view(rows)
        sched_chips, sched_scroll = _build_schedule_view()

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
                    Div(
                        sched_chips, sched_scroll,
                        id="view-schedule", cls="view-pane",
                        **{"data-view": "schedule"},
                    ),
                    cls="view-area",
                ),
                _date_modal(),
                _settings_modal(employees),
                _day_detail_modal(),
                _procedure_modal(),
                cls="app-shell",
            )],
            extra_scripts=[
                Script(src="/static/portal_modal.js", defer=True),
                Script(src="/static/staging_edit_modal.js", defer=True),
                _client_script(employees, corpus, roster, date_min, date_max),
            ],
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

    @rt("/staging_task_board/fill_driving", methods=["POST"])
    async def fill_driving(request: Request):
        """Fill missing Driving_Time on the requested staging IDs by hitting
        Google Distance Matrix. Writes back to local Staging_Report (not
        pushed to Zoho per current read-only mode). Returns a per-sid
        minutes map; null means no API key, no address, or API failure —
        client falls back to a 30-minute estimate."""
        form = await request.form()
        sids_raw = (form.get("sids") or "").strip()
        sids = [s.strip() for s in sids_raw.split(",") if s.strip()]
        if not sids:
            return JSONResponse({"results": {}})
        out: dict = {}
        with _conn() as c:
            placeholders = ",".join(["?"] * len(sids))
            rows = c.execute(
                f"SELECT ID, Staging_Address, Driving_Time FROM Staging_Report "
                f"WHERE ID IN ({placeholders})",
                sids,
            ).fetchall()
            for r in rows:
                rid = str(r["ID"])
                existing = (r["Driving_Time"] or "").strip()
                if existing:
                    try:
                        out[rid] = int(existing)
                        continue
                    except Exception:
                        pass
                addr = _parse_link(r["Staging_Address"])
                if not addr:
                    out[rid] = None
                    continue
                mins = _fetch_drive_minutes(_WAREHOUSE_ADDRESS, addr)
                if mins is None:
                    out[rid] = None
                    continue
                c.execute(
                    "UPDATE Staging_Report SET Driving_Time = ? WHERE ID = ?",
                    (str(mins), rid),
                )
                out[rid] = mins
            c.commit()
        return JSONResponse({"results": out})

    @rt("/staging_task_board/save_assignment", methods=["POST"])
    async def save_assignment(request: Request):
        """Persist a schedule-view assignment back to Staging_Report.
        Local-only — no Zoho push (matches read-only mode in
        as_webapp/main.py). Synthetic Design+Packing cards (sid ends in
        '_dp') skip the write because they have no DB row."""
        form = await request.form()
        sid = (form.get("sid") or "").strip()
        kind = (form.get("kind") or "").strip()
        # Accept legacy single "stager" or array-style "stagers" (pipe-delimited).
        stagers_raw = (form.get("stagers")
                       or form.get("stager")
                       or "").strip()
        stagers = [s.strip() for s in stagers_raw.split("|") if s.strip()]
        movers_raw = (form.get("movers") or "").strip()
        movers = [m.strip() for m in movers_raw.split("|") if m.strip()]

        if not sid or sid.endswith("_dp") or kind == "Design":
            return JSONResponse({"ok": True, "skipped": True})

        # Map kind → columns. Staging touches both stagers + movers;
        # destage only movers; consultation only the consult stager(s).
        stager_col = None
        movers_col = None
        if kind == "Staging":
            stager_col = "Stager"
            movers_col = "Staging_Movers"
        elif kind == "Destage":
            movers_col = "Destaging_Movers"
        elif kind == "Consultation":
            stager_col = "Consultation_Stager1"
        else:
            return JSONResponse({"ok": True, "skipped": True})

        updates = {}
        if stager_col is not None:
            arr = [_person_json_obj(s) for s in stagers]
            updates[stager_col] = json.dumps(arr)
        if movers_col is not None:
            arr = [_person_json_obj(m) for m in movers]
            updates[movers_col] = json.dumps(arr)

        if not updates:
            return JSONResponse({"ok": True, "skipped": True})

        sets = ", ".join(f"{col} = ?" for col in updates)
        params = list(updates.values()) + [sid]
        with _conn() as c:
            c.execute(
                f"UPDATE Staging_Report SET {sets} WHERE ID = ?", params,
            )
            c.commit()
        return JSONResponse({"ok": True, "updated": list(updates.keys())})

    # -------- portal staging modal API (used by static/staging_edit_modal.js) --------
    # GET returns the editable record + roster. POST applies a diff. Local DB
    # only — same write model as set_date / save_assignment (no Zoho push).

    @rt("/portal/staging/{staging_id}")
    def portal_staging_get(staging_id: str):
        with _conn() as c:
            row = c.execute(
                "SELECT * FROM Staging_Report WHERE ID = ?", (staging_id,),
            ).fetchone()
        if not row:
            return JSONResponse({"error": "not found"}, status_code=404)
        return JSONResponse(_staging_modal_payload(row))

    @rt("/portal/staging/{staging_id}/save", methods=["POST"])
    async def portal_staging_save(request: Request, staging_id: str):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "invalid json"}, status_code=400)
        patch = body.get("patch") or {}
        if not isinstance(patch, dict) or not patch:
            return JSONResponse({"error": "empty patch"}, status_code=400)

        rejected, updates = [], {}
        for k, v in patch.items():
            if k not in _STAGING_EDITABLE_FIELDS:
                rejected.append(k)
                continue
            updates[k] = _serialize_staging_field(k, v)
        if not updates:
            return JSONResponse({"error": "no editable fields", "rejected": rejected},
                                status_code=400)

        sets = ", ".join(f"{col} = ?" for col in updates)
        params = list(updates.values()) + [staging_id]
        with _conn() as c:
            cur = c.execute(
                f"UPDATE Staging_Report SET {sets} WHERE ID = ?", params,
            )
            c.commit()
            if cur.rowcount == 0:
                return JSONResponse({"error": "not found"}, status_code=404)
            row = c.execute(
                "SELECT * FROM Staging_Report WHERE ID = ?", (staging_id,),
            ).fetchone()
        return JSONResponse({
            "ok": True,
            "updated": list(updates.keys()),
            "rejected": rejected,
            "record": _staging_modal_payload(row),
        })

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
