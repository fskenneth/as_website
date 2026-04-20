"""
Staging Task Board — FastHTML port of Zoho's Staging_Task_Board page.

Reads from data/zoho_sync.db.Staging_Report (Zoho snapshot; auto-sync is
paused during UI-design phase — see project_sync_intervals_to_restore memory).

Field updates write straight to Staging_Report. No Zoho push; changes stay
local so web/iOS/Android all see each other. When Zoho is deprecated,
zoho_sync.db becomes the primary DB and these writes become authoritative.

Pattern for row buttons: an HTML form POSTs to a local handler, handler
writes the field, then 302 redirects back to /staging_task_board. No
JavaScript needed — matches the Zoho URL-based pattern but cleaner.

Sub-pages (Staging_Design, Packing_Guide, etc.) land on /stub?page=X&...
until ported; see as_webapp/UNPORTED_PAGES.md for the queue.
"""
from datetime import date, datetime, timedelta
import json
import os
import sqlite3
from urllib.parse import urlencode

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, Input, Li, Ol, P, Span, Style,
    Table, Tbody, Td, Th, Thead, Tr, Titled, Ul, NotStr,
)
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

# Which URL param -> DB column value mapping for period filter.
_PERIOD_RANGES = {
    "today_only": lambda today: (today, today + timedelta(days=1)),
    "this_week":  lambda today: (today + timedelta(days=-5), today + timedelta(days=14)),
    "anytime":    lambda today: (today + timedelta(days=-1000), today + timedelta(days=365)),
}


# -------------------- helpers --------------------

def _conn():
    c = sqlite3.connect(ZOHO_DB)
    c.row_factory = sqlite3.Row
    return c


def _parse_mdy(s: str | None):
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except Exception:
        return None


def _fmt_mdy(d: date) -> str:
    return d.strftime("%m/%d/%Y")


def _parse_people(s: str | None):
    """Zoho multi-select returns JSON array of {display_value, ID}."""
    if not s or not s.strip():
        return []
    try:
        arr = json.loads(s)
        return [p.get("display_value", "") for p in arr if isinstance(p, dict) and p.get("display_value")]
    except Exception:
        return []


def _parse_link(s: str | None):
    """Zoho lookup column returns JSON object {display_value, ID}."""
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


def _weekday_abbr(d: date) -> str:
    return d.strftime("%a")  # Mon, Tue, ...


# -------------------- data fetch --------------------

def _fetch_stagings(period: str, show_my: bool, show_stars: bool, my_name: str | None):
    """Read Staging_Report rows in [from_date, to_date) sorted by
    Coming_Staging_Destaging_Date. Returns list of sqlite3.Row.
    """
    today = date.today()
    from_d, to_d = _PERIOD_RANGES.get(period, _PERIOD_RANGES["this_week"])(today)

    # Staging_Date / Destaging_Date are MM/dd/yyyy strings; build ISO expression
    # for correct chronological ordering. Coming_Staging_Destaging_Date is the
    # pre-computed "whichever is relevant for this row" date, also MM/dd/yyyy.
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
    if show_stars:
        # Zoho marks starred via ">*" inside Staging_Table_Row_HTML. The local
        # DB doesn't populate that field yet, so skip this filter for now.
        pass

    return rows, from_d, to_d, today


def _is_mine(row, needle: str) -> bool:
    """Staging is 'mine' if user's first name appears in Stager / Movers /
    Destaging_Movers. Logic matches Zoho page:9736."""
    fields = (row["Stager"], row["Staging_Movers"], row["Destaging_Movers"])
    for f in fields:
        for name in _parse_people(f):
            if name and needle in name.lower():
                return True
    return False


def _group_by_date(rows):
    """Zoho renders a yellow header row per unique Coming_Staging_Destaging_Date.
    Returns list of (date_str, [row, row, ...])."""
    out = []
    current = None
    group = []
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


# -------------------- HTML primitives --------------------

def _css():
    """Replicates the Zoho page styling from .ds:9945+."""
    return Style("""
    .task-board-wrap { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; color: #222; }
    .task-board-toolbar { padding: 10px 14px; background: #f4f6fa; border-bottom: 1px solid #d0d7de; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .task-board-toolbar a.btn {
        display: inline-block; padding: 6px 12px;
        border: 1px solid #aab2bd; border-radius: 6px;
        background: #fff; color: #24292e; font-size: 13px;
        text-decoration: none; cursor: pointer;
    }
    .task-board-toolbar a.btn:hover { background: #f0f2f5; }
    .task-board-toolbar a.btn.active { background: #cfe3ff; border-color: #5d9bd7; }

    table.zc-viewtable { width: 100%; border-collapse: collapse; font-size: 12px; background: #fff; }
    table.zc-viewtable td, table.zc-viewtable th { border: 1px solid rgb(93,155,215); padding: 6px 8px; vertical-align: top; }

    tr.zc-viewrowheader-template { background: rgb(127,190,251); color: #fff; font-weight: 600; }
    tr.zc-viewrowheader-template th { padding: 8px; text-align: left; font-size: 13px; }

    tr.zc-row-1 td { background: #ffffff; }
    tr.zc-row-2 td { background: rgb(240,230,140); }
    tr.zc-row-3 td { background: rgb(255,160,122); }
    tr.zc-row-4 td { background: rgb(0,255,20); }
    tr.zc-row-5 td { background: rgb(192,192,192); }
    tr.zc-row-6 td { background: rgb(255,153,204); }
    tr.zc-row-7 td { background: rgb(102,178,255); }
    tr.zc-row-8 td {
        background: rgb(255,255,0);
        font-weight: bold; font-size: 1.4em;
        text-align: center; border: 4px solid #000; padding: 10px;
    }

    .row-btn {
        display: inline-block; padding: 4px 9px; margin: 2px 0;
        border: 1px solid #8892a0; border-radius: 5px; background: #fafbfc;
        color: #24292e; font-size: 12px; cursor: pointer; text-decoration: none;
    }
    .row-btn:hover { background: #eef2f7; }
    .row-btn.done { background: #d4edda; color: #155724; border-color: #87c397; }

    .row-link { color: #1565c0; text-decoration: none; }
    .row-link:hover { text-decoration: underline; }

    .col { min-width: 260px; max-width: 280px; white-space: normal; }
    .col-narrow { min-width: 160px; max-width: 180px; white-space: normal; }
    .staging-title strong { font-weight: 600; }
    .empty-placeholder td { background: #fafafa; color: #999; font-style: italic; }

    .mobile-card {
        padding: 10px 12px; border-bottom: 2px solid #d0d7de;
        white-space: normal; font-size: 13px;
    }
    .mobile-card strong { font-weight: 600; }
    """)


def _toolbar(display_mode: str, show_period: str, show_my: bool, qs: dict):
    """Toolbar buttons — each is an <a> that re-navigates to the page with
    updated query params. Mirrors Zoho .ds:9708+.
    """
    def link(params: dict, label: str, active: bool = False):
        merged = {**qs, **params}
        # cosmetic cleanup: drop empty params from URL
        merged = {k: v for k, v in merged.items() if v not in (None, "")}
        href = "/staging_task_board"
        if merged:
            href += "?" + urlencode(merged)
        return A(label, href=href, cls="btn active" if active else "btn")

    period_buttons = []
    if show_period == "today_only":
        period_buttons = [
            link({"show_period": "anytime"}, "Show All Days"),
            link({"show_period": "this_week"}, "Show Week"),
        ]
    elif show_period == "this_week":
        period_buttons = [
            link({"show_period": "anytime"}, "Show All Days"),
            link({"show_period": "today_only"}, "Show Today"),
        ]
    else:  # anytime
        period_buttons = [
            link({"show_period": "today_only"}, "Show Today"),
            link({"show_period": "this_week"}, "Show Week"),
        ]

    display_btn = (
        link({"display": "desktop"}, "To Desktop") if display_mode == "mobile"
        else link({"display": "mobile"}, "To Mobile")
    )

    my_btn = (
        link({"show_only_my_tasks": "no"}, "Show All Tasks", active=True)
        if show_my
        else link({"show_only_my_tasks": "yes"}, "Show Only My Tasks")
    )

    return Div(display_btn, *period_buttons, my_btn, cls="task-board-toolbar")


def _sub_page_link(label: str, page: str, **params):
    """A link to a sub-page stub. All sub-pages land on /stub for now."""
    q = {"page": page, **{k: v for k, v in params.items() if v}}
    return A(label, href="/stub?" + urlencode(q), target="_blank", cls="row-link")


def _date_button(staging_id: str, field: str, label: str, currently_done: bool):
    """'Mark as done today' button. Submits a POST form to
    /staging_task_board/set_date. Matches Zoho pattern but doesn't rely on
    URL side-effects — cleaner HTML form semantics.
    """
    return Form(
        Button(label, type="submit", cls=f"row-btn {'done' if currently_done else ''}"),
        Input(type="hidden", name="staging_id", value=staging_id),
        Input(type="hidden", name="field", value=field),
        method="POST",
        action="/staging_task_board/set_date",
        style="display:inline-block;margin:0",
    )


def _clear_date_button(staging_id: str, field: str, label: str):
    """Companion 'undo' — clears the date field."""
    return Form(
        Button(label, type="submit", cls="row-btn"),
        Input(type="hidden", name="staging_id", value=staging_id),
        Input(type="hidden", name="field", value=field),
        Input(type="hidden", name="clear", value="1"),
        method="POST",
        action="/staging_task_board/set_date",
        style="display:inline-block;margin:0",
    )


# -------------------- column renderers --------------------

def _col_staging(row, serial: int):
    """Column 1: date, staging label, remaining days, address, sub-page links."""
    date_s = row["Coming_Staging_Destaging_Date"] or ""
    d = _parse_mdy(date_s)
    date_head = f"{d.strftime('%b %d %a')}" if d else date_s

    occ = row["Occupancy_Type"] or ""
    prop = row["Property_Type"] or ""
    sd = _parse_mdy(row["Staging_Date"])
    dd = _parse_mdy(row["Destaging_Date"])
    today = date.today()

    # "Staging N" or "Destaging N" depending on which date matches today's row
    is_destage = dd and d == dd and (not sd or sd != dd)
    kind_label = "Destaging" if is_destage else "Staging"

    # "[30 Remaining / 22 in Design]"
    remaining_days = None
    if sd and dd:
        remaining_days = (dd - max(sd, today)).days if today >= sd else (dd - sd).days
    item_count = row["Total_Item_Number"] or 0
    try:
        item_count_str = str(int(str(item_count).split(".")[0])) if item_count else "0"
    except Exception:
        item_count_str = "0"
    remain_str = f"[{remaining_days if remaining_days is not None else '?'} Remaining / {item_count_str} in Design]"

    address = _parse_link(row["Staging_Address"]) or row["Staging_Display_Name"] or ""
    eta = row["Staging_ETA"] or ""
    drive = row["Driving_Time"] or ""
    meta_bits = [x for x in (eta, drive + (" mins" if drive else "")) if x]

    return Td(
        Span(f"{date_head} "),
        Span(f"{occ + ' ' if occ else ''}{prop + ' ' if prop else ''}".strip()),
        NotStr(" <strong>"), NotStr(f"{kind_label} {serial}"), NotStr("</strong>"),
        NotStr("<br>"),
        NotStr(remain_str),
        NotStr("<br>"),
        NotStr("<strong>"), NotStr(address or "—"), NotStr("</strong>"),
        *( [Span(" " + " ".join(meta_bits))] if meta_bits else [] ),
        NotStr("<br>"),
        A("Edit", href=f"/stub?{urlencode({'page':'Staging_Edit','staging_id':row['ID']})}", cls="row-link"),
        NotStr(" | "),
        _sub_page_link("Design", "Staging_Design", staging_id=row["ID"]),
        NotStr(" | "),
        _sub_page_link("Pictures", "Staging_Videos_and_Pictures", staging_id=row["ID"]),
        NotStr(" | "),
        _sub_page_link("Packing", "Packing_Guide_Page", staging_id=row["ID"], staging_type="Staging"),
        NotStr(" | "),
        _sub_page_link("Setup", "Staging_Setup_Guide", staging_id=row["ID"]),
        cls="col",
    )


def _col_persons(row):
    cust_fn = row["Customer_First_Name"] or ""
    cust_ln = row["Customer_Last_Name"] or ""
    customer = f"{cust_fn} {cust_ln}".strip() or "—"
    stagers = ", ".join(_parse_people(row["Stager"])) or ""
    movers = ", ".join(_parse_people(row["Staging_Movers"])) or ""
    destage_movers = ", ".join(_parse_people(row["Destaging_Movers"])) or ""
    return Td(
        NotStr(f"Customer: {customer}<br>"),
        NotStr(f"Stager: <strong>{stagers}</strong><br>"),
        NotStr(f"Staging Movers: <strong>{movers}</strong>"),
        *([NotStr(f"<br>Destaging Movers: <strong>{destage_movers}</strong>")] if destage_movers else []),
        cls="col",
    )


def _col_actions(row):
    """Column 3: milestone chip row + 'mark done' buttons for each date field.
    In Zoho this column holds task-assignee buttons that are dynamically
    built from Module records; we render the ones that land on the
    Staging itself.
    """
    sid = row["ID"]
    milestones = [
        ("Design", "Design_Items_Matched_Date"),
        ("Before Pics", "Before_Picture_Upload_Date"),
        ("After Pics", "After_Picture_Upload_Date"),
        ("Packing", "Staging_Accessories_Packing_Finish_Date"),
        ("Setup", "Staging_Furniture_Design_Finish_Date"),
        ("WhatsApp", "WhatsApp_Group_Created_Date"),
        ("Next Steps", "Next_Steps_Email_Sent_Date"),
        ("Basement Check", "Check_Basement_Furniture_Size_Date"),
    ]
    chips = []
    for label, field in milestones:
        val = row[field]
        done = bool(val and val.strip())
        chip_label = f"{label} ✓" if done else label
        chips.append(_date_button(sid, field, chip_label, done))
    return Td(*chips, cls="col")


def _col_moving(row):
    return Td(
        NotStr(row["Staging_Moving_Instructions"] or ""),
        cls="col",
    )


def _col_notes(row):
    # Zoho stores General_Notes as a long multi-line string with embedded newlines
    notes = (row["General_Notes"] or "").replace("\n", "<br>")
    return Td(NotStr(notes), cls="col")


def _col_accounting(row):
    sid = row["ID"]
    total = _money(row["Total_Staging_Fee"])
    paid = _money(row["Paid_Amount"])
    owing = _money(row["Owing_Amount"])
    owing_color = "color:#c62828;" if owing > 0 else ""
    return Td(
        NotStr(f"Staging Fee: ${total:,.2f}<br>"),
        NotStr(f"Paid: ${paid:,.2f}<br>"),
        NotStr(f"<span style='{owing_color}'>Owing: ${owing:,.2f}</span><br>"),
        A("Payment History", href=f"/stub?{urlencode({'page':'Payment_Report','staging_id':sid})}", target="_blank", cls="row-link"),
        NotStr("<br>"),
        A(Button("Download Invoice", cls="row-btn"), href=f"/stub?{urlencode({'page':'Staging_Invoice','staging_id':sid})}", target="_self"),
        NotStr(" "),
        A(Button("Send Invoice", cls="row-btn"), href=f"/stub?{urlencode({'page':'Email_Generator','staging_id':sid,'email_type':'Payment Notification'})}", target="_self"),
        NotStr("<br>"),
        _date_button(sid, "Invoice_Sent_Date", "Invoice Sent ✓" if row["Invoice_Sent_Date"] else "Mark Invoice Sent", bool(row["Invoice_Sent_Date"])),
        cls="col",
    )


def _col_listing(row):
    sid = row["ID"]
    pics_folder = row["Pictures_Folder"] or ""
    mls = row["MLS"] or ""
    housesigma = row["HouseSigma_URL"] or ""

    elements = []
    if pics_folder:
        elements.append(A(Button("Upload Pictures to Google Drive", cls="row-btn"), href=pics_folder, target="_blank"))
        elements.append(NotStr("<br>"))
    # After Picture Uploaded toggle
    ap_done = bool(row["After_Picture_Upload_Date"])
    elements.append(_date_button(sid, "After_Picture_Upload_Date", "After Pics Uploaded ✓" if ap_done else "After Picture Uploaded", ap_done))
    elements.append(NotStr("<br>"))
    if mls:
        elements.append(Span(f"MLS: {mls}"))
        elements.append(NotStr("<br>"))
    if housesigma:
        elements.append(A("HouseSigma", href=housesigma, target="_blank", cls="row-link"))
        elements.append(NotStr("<br>"))
    elements.append(A(Button("Update MLS Info", cls="row-btn"), href=f"/stub?{urlencode({'page':'Staging_Edit','staging_id':sid,'focus':'MLS'})}", target="_self"))
    return Td(*elements, cls="col-narrow")


def _row_class(row) -> str:
    """Approximates Zoho's row coloring. Real rules live across multiple
    workflow functions we don't fully have; these heuristics match the
    obvious cases visible in the screenshots.
    """
    today = date.today()
    status = (row["Staging_Status"] or "").lower()
    sd = _parse_mdy(row["Staging_Date"])
    dd = _parse_mdy(row["Destaging_Date"])
    coming = _parse_mdy(row["Coming_Staging_Destaging_Date"])

    if status == "inquired":
        return "zc-row-5"  # gray
    if dd and coming and dd == coming:
        return "zc-row-2"  # destaging → khaki
    if coming == today:
        return "zc-row-7"  # today → light blue
    return "zc-row-1"  # default white


def _desktop_table(grouped, from_d: date, to_d: date, today: date):
    """Render the full desktop table with date-header rows + staging rows
    + placeholder rows for empty weekdays.
    """
    header = Tr(
        Th(NotStr("Staging <a href='/stub?page=Staging_Form' target='_self' class='row-link'>[New Staging]</a> <a href='/stub?page=Module_Form' target='_self' class='row-link'>[New Task]</a>")),
        Th("Persons"),
        Th("Actions"),
        Th("Moving Instructions"),
        Th("General Notes"),
        Th("Accounting"),
        Th("Listing"),
        cls="zc-viewrowheader-template",
    )

    # Build a date → group index for quick lookup
    by_date = {}
    for date_str, group in grouped:
        d = _parse_mdy(date_str)
        if d:
            by_date[d] = (date_str, group)

    body_rows = []
    # Walk the range day by day so empty days still show a header
    d = from_d
    while d < to_d:
        if d in by_date:
            date_str, group = by_date[d]
            # Yellow date header
            pretty = d.strftime("%B %d %A")
            body_rows.append(Tr(
                Td(pretty, colspan="7"),
                cls="zc-row-8",
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
                    cls=f"zc-viewrow {_row_class(r)}",
                ))
        else:
            # Only show empty-day header on weekdays (Mon-Fri = 0..4)
            if d.weekday() < 5 and from_d <= d <= to_d:
                pretty = d.strftime("%B %d %A")
                body_rows.append(Tr(
                    Td(pretty, colspan="7"),
                    cls="zc-row-8",
                ))
                # 6 capacity slots per day
                for i in range(6):
                    body_rows.append(Tr(
                        Td(NotStr(f"<em>Staging/Destaging slot {i+1} available</em>"), colspan="7"),
                        cls="zc-viewrow empty-placeholder",
                    ))
        d += timedelta(days=1)

    return Table(Thead(header), Tbody(*body_rows), cls="zc-viewtable")


def _mobile_cards(grouped, from_d: date, to_d: date):
    cards = []
    by_date = {_parse_mdy(k): (k, g) for k, g in grouped}
    by_date.pop(None, None)

    d = from_d
    while d < to_d:
        if d in by_date:
            date_str, group = by_date[d]
            cards.append(Div(d.strftime("%B %d %A"), cls="mobile-card", style="background:#ff0;font-weight:bold;text-align:center;font-size:1.2em;border:2px solid #000;"))
            for i, r in enumerate(group, start=1):
                cards.append(Div(
                    NotStr(f"<strong>{d.strftime('%b %d %a')} {r['Occupancy_Type'] or ''} {r['Property_Type'] or ''} Staging {i}</strong><br>"),
                    NotStr(f"{_parse_link(r['Staging_Address']) or r['Staging_Display_Name'] or '—'}<br>"),
                    NotStr(f"Customer: {(r['Customer_First_Name'] or '') + ' ' + (r['Customer_Last_Name'] or '')}<br>"),
                    NotStr(f"Stager: <strong>{', '.join(_parse_people(r['Stager']))}</strong><br>"),
                    NotStr(f"Movers: <strong>{', '.join(_parse_people(r['Staging_Movers']))}</strong><br>"),
                    _sub_page_link("Design", "Staging_Design", staging_id=r["ID"]),
                    NotStr(" | "),
                    _sub_page_link("Pictures", "Staging_Videos_and_Pictures", staging_id=r["ID"]),
                    NotStr(" | "),
                    _sub_page_link("Packing", "Packing_Guide_Page", staging_id=r["ID"]),
                    NotStr(" | "),
                    _sub_page_link("Setup", "Staging_Setup_Guide", staging_id=r["ID"]),
                    cls="mobile-card",
                ))
        d += timedelta(days=1)
    return Div(*cards)


# -------------------- route registration --------------------

def register(rt):
    """Attach /staging_task_board routes to the given FastHTML router."""

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
        # my_name would ideally come from the logged-in user; for now we
        # accept it as a URL param since auth is disabled per the spec.
        # No default → show_my=True with blank my_name returns nothing.
        my_name = (my_name or "").strip()

        rows, from_d, to_d, today = _fetch_stagings(period, show_my, stars, my_name)
        grouped = _group_by_date(rows)

        qs = {
            "display": display_mode if display_mode != "desktop" else "",
            "show_period": period if period != "this_week" else "",
            "show_only_my_tasks": "yes" if show_my else "",
            "show_stars": "yes" if stars else "",
            "my_name": my_name,
        }

        body = (
            _mobile_cards(grouped, from_d, to_d)
            if display_mode == "mobile"
            else _desktop_table(grouped, from_d, to_d, today)
        )

        return Titled(
            "Staging Task Board",
            _css(),
            _toolbar(display_mode, period, show_my, qs),
            Div(
                P(NotStr(f"<small>Range: {from_d.isoformat()} → {to_d.isoformat()} · "
                         f"{len(rows)} stagings loaded · today {today.isoformat()}</small>")),
                body,
                cls="task-board-wrap",
            ),
        )

    @rt("/staging_task_board/set_date", methods=["POST"])
    async def set_date(request: Request):
        """Toggle a Staging_Report date field. Form body:
        staging_id, field [, clear=1].
        Writes directly to local zoho_sync.db. No Zoho push.
        """
        form = await request.form()
        sid = (form.get("staging_id") or "").strip()
        field = (form.get("field") or "").strip()
        clear = form.get("clear") == "1"

        if not sid or field not in _DATE_FIELDS:
            return RedirectResponse("/staging_task_board?error=bad_params", status_code=303)

        if field.endswith("_Time"):
            # Timestamp fields (e.g. Consultation_Notes_Complete_Time) use current time
            new_value = "" if clear else datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        else:
            new_value = "" if clear else _fmt_mdy(date.today())

        with _conn() as c:
            c.execute(f"UPDATE Staging_Report SET {field} = ? WHERE ID = ?", (new_value, sid))
            c.commit()

        # Preserve the toolbar state on the redirect
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
        """Placeholder for any Zoho sub-page the task board links to."""
        params = dict(request.query_params)
        page = params.pop("page", "Unknown")
        return Titled(
            f"Not yet ported — {page}",
            Div(
                H1(f"Sub-page stub: {page}"),
                P("This page is linked from the Staging Task Board but hasn't been ported yet."),
                P(NotStr("<strong>Params received:</strong>")),
                Ul(*[Li(NotStr(f"<code>{k}</code> = <code>{v}</code>")) for k, v in params.items()]) if params else P("(no params)"),
                P(A("← Back to Task Board", href="/staging_task_board", cls="row-link")),
                style="padding:24px; font-family:-apple-system,sans-serif;",
            ),
            _css(),
        )
