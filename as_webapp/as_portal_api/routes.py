"""
/api/v1/* — Bearer-token API for iOS and Android clients.

Extracted from as_website/main.py during the as_webapp split. Contract is
unchanged; only the auth backend now points at data/employees.db (not
data/users.db) and writes to pending_zoho_updates via plain sqlite3
(the drainer running in main.py — or later in as_webapp — picks them up).
"""
from datetime import date, datetime, timedelta
import json
import mimetypes
import os
import re
import sqlite3
import uuid

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from . import employees_db

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZOHO_DB_PATH = os.path.join(ROOT, "data", "zoho_sync.db")
MEDIA_ROOT = os.path.join(ROOT, "data", "staging_media")

# Zoho Area_Name values are prefixed with an ordering token ("01 Living Room",
# "11 Sales Office 02") — strip the leading digits so the UI shows clean names.
_AREA_PREFIX_RE = re.compile(r"^\s*\d{1,3}\s+")


def _strip_area_prefix(name):
    if not name:
        return ""
    return _AREA_PREFIX_RE.sub("", str(name)).strip()


def _ensure_media_table():
    """Create media_uploads on first import. Idempotent."""
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    conn = sqlite3.connect(ZOHO_DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_uploads (
                id TEXT PRIMARY KEY,
                staging_id TEXT NOT NULL,
                area_id TEXT,
                area_name TEXT,
                media_type TEXT NOT NULL,
                client_id TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                uploaded_by TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                zoho_synced INTEGER DEFAULT 0,
                notes TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_media_uploads_staging "
            "ON media_uploads(staging_id)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_media_uploads_client "
            "ON media_uploads(client_id) WHERE client_id IS NOT NULL"
        )
        conn.commit()
    finally:
        conn.close()


_ensure_media_table()


def _ensure_dictation_table():
    """Create consultation_dictations on first import. Idempotent.

    One row per completed voice dictation. Stores the audio file path, the
    Whisper transcript, and the gpt-4o-mini structured summary (emails + key
    points + suggested quote lines) as JSON. `sent_emails_json` records which
    drafts were sent via Mailgun so the UI can show a history.
    """
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    conn = sqlite3.connect(ZOHO_DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultation_dictations (
                id TEXT PRIMARY KEY,
                staging_id TEXT NOT NULL,
                area_id TEXT,
                area_name TEXT,
                client_id TEXT,
                audio_path TEXT NOT NULL,
                audio_size INTEGER,
                duration_sec REAL,
                transcript TEXT,
                summary_json TEXT,
                status TEXT DEFAULT 'processing',
                error TEXT,
                sent_emails_json TEXT,
                uploaded_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dictations_staging "
            "ON consultation_dictations(staging_id)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_dictations_client "
            "ON consultation_dictations(client_id) WHERE client_id IS NOT NULL"
        )
        conn.commit()
    finally:
        conn.close()


_ensure_dictation_table()


def _ensure_line_items_table():
    """Create consultation_line_items on first import. Idempotent.

    Each row is a tap in the consultation item picker. `action` is 'add'
    (goes on the new-furniture list for the quote) or 'remove' (existing
    items the client wants removed). Uniqueness on (staging, area, action,
    item) so a second tap upserts the quantity instead of inserting twice.
    """
    conn = sqlite3.connect(ZOHO_DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultation_line_items (
                id TEXT PRIMARY KEY,
                staging_id TEXT NOT NULL,
                area_id TEXT NOT NULL,
                action TEXT NOT NULL,
                item_name TEXT NOT NULL,
                unit_price REAL DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 1,
                updated_by TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_line_items_unique "
            "ON consultation_line_items(staging_id, area_id, action, item_name)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_line_items_staging "
            "ON consultation_line_items(staging_id)"
        )
        conn.commit()
    finally:
        conn.close()


_ensure_line_items_table()


# ---------------- quote catalog + pricing ----------------
# Mirrors page/staging_inquiry.py (items_data + getBaseFee + getAreaPrice).
# Single source of truth for mobile consultations; if the website's list
# diverges meaningfully, reconcile here before shipping.

_QUOTE_CATALOG = [
    ("Sofa", 250), ("Accent Chair", 100), ("Coffee Table", 100),
    ("End Table", 50), ("Console", 75), ("Bench", 65),
    ("Area Rug", 80), ("Lamp", 40), ("Cushion", 15),
    ("Throw", 18), ("Table Decor", 10), ("Wall Art", 40),
    ("Formal Dining Set", 400), ("Bar Stool", 40),
    ("Casual Dining Set", 250), ("Queen Bed Frame", 20),
    ("Queen Headboard", 90), ("Queen Mattress", 50),
    ("Queen Beddings", 120), ("King Bed Frame", 20),
    ("King Headboard", 130), ("King Mattress", 50),
    ("King Beddings", 150), ("Double Bed Frame", 20),
    ("Double Headboard", 80), ("Double Mattress", 50),
    ("Double Bedding", 120), ("Night Stand", 60),
    ("Single Bed Frame", 20), ("Single Headboard", 75),
    ("Single Mattress", 50), ("Single Beddings", 80),
    ("Desk", 100), ("Chair", 50), ("Patio Set", 150),
]
_QUOTE_CATALOG_MAP = {name: price for name, price in _QUOTE_CATALOG}

BASE_STAGING_FEE = 1450.0
HUGE_AREA = 700.0
BIG_AREA = 500.0
SMALL_AREA = 200.0

# Default property size when Staging_Report doesn't carry sqft. Matches the
# bulk-of-real-properties bucket and keeps base fee +$200.
_DEFAULT_PROPERTY_SIZE = "1000-2000"


def _base_fee_for_size(property_size: str) -> float:
    if property_size in ("2000-3000", "3000-4000", "over-4000"):
        return BASE_STAGING_FEE + 800
    if property_size == "1000-2000":
        return BASE_STAGING_FEE + 200
    return BASE_STAGING_FEE


def _area_key_from_name(area_name: str) -> str:
    """Map a Zoho Area_Name (stripped) to a staging_inquiry area key so
    we can reuse getAreaPrice's cap logic."""
    n = _strip_area_prefix(area_name).lower().strip()
    if not n:
        return "other"
    # Direct substring mapping — Zoho names include "Living Room",
    # "Bedroom King", "Basement Living", "Breakfast Area", etc.
    if "basement" in n:
        if "living" in n: return "basement-living"
        if "dining" in n: return "basement-dining"
        if "office" in n: return "basement-office"
        if "bedroom" in n or "bed" in n: return "basement-1st-bedroom"
        return "basement-living"
    if "living" in n: return "living-room"
    if "family" in n: return "family-room"
    if "dining" in n: return "dining-room"
    if "breakfast" in n: return "breakfast-area"
    if "kitchen" in n and "island" in n: return "kitchen-island"
    if "kitchen" in n: return "kitchen-only"
    if "bathroom" in n: return "bathrooms"
    if "office" in n or "study" in n: return "office"
    if "patio" in n or "outdoor" in n or "deck" in n: return "outdoor"
    # Bedrooms — treat the first named bedroom as master unless clearly 2nd+
    if "bedroom" in n or "bed" in n:
        for tok, key in (("2nd", "2nd-bedroom"), ("3rd", "3rd-bedroom"),
                         ("4th", "4th-bedroom"), ("5th", "5th-bedroom"),
                         ("6th", "6th-bedroom")):
            if tok in n:
                return key
        return "master-bedroom"
    return "other"


def _area_cap(area_key: str, property_type: str, property_size: str) -> float:
    """Bulk cap for a single area. Matches getAreaPrice() in staging_inquiry.py."""
    pt = (property_type or "").lower()
    is_large_house = pt == "house" and property_size in ("3000-4000", "over-4000")
    is_small_condo = pt == "condo" and property_size == "under-1000"

    if area_key == "living-room":
        return HUGE_AREA if is_large_house else BIG_AREA
    if area_key == "dining-room":
        if is_small_condo: return SMALL_AREA
        return HUGE_AREA if is_large_house else BIG_AREA
    if area_key == "family-room":
        return HUGE_AREA if is_large_house else BIG_AREA
    if area_key == "kitchen-only":
        return 0
    if area_key == "kitchen-island":
        if is_small_condo: return 100
        return 300 if is_large_house else 200
    if area_key == "breakfast-area":
        return SMALL_AREA
    if area_key == "master-bedroom":
        if is_small_condo: return SMALL_AREA
        return HUGE_AREA if is_large_house else BIG_AREA
    if area_key == "2nd-bedroom":
        return BIG_AREA if is_large_house else SMALL_AREA
    if area_key in ("3rd-bedroom", "4th-bedroom", "5th-bedroom", "6th-bedroom"):
        return SMALL_AREA
    if area_key == "office":
        return BIG_AREA if is_large_house else SMALL_AREA
    if area_key == "bathrooms":
        return 0
    if area_key == "basement-living":
        return BIG_AREA
    if area_key in ("basement-dining", "basement-1st-bedroom",
                    "basement-2nd-bedroom", "basement-office"):
        return SMALL_AREA
    if area_key == "outdoor":
        return 150
    return BIG_AREA  # sensible default for "New Area" / unknown


def _compute_staging_quote(conn: sqlite3.Connection, staging_id: str) -> dict:
    """Return the full live quote for a staging: per-area add/remove lists,
    per-area cap + effective subtotal, and the grand total."""
    staging_row = conn.execute(
        "SELECT Property_Type FROM Staging_Report WHERE ID = ?",
        (staging_id,),
    ).fetchone()
    property_type = (staging_row["Property_Type"] if staging_row else "") or ""
    property_size = _DEFAULT_PROPERTY_SIZE

    area_rows = conn.execute(
        """
        SELECT ID, Area_Name, Area_Display_Name, Staging
        FROM Area_Report
        WHERE _sync_status != 'deleted'
          AND (Delete_Area IS NULL OR Delete_Area = '' OR Delete_Area = 'false')
          AND Staging LIKE ?
        """,
        (f"%{staging_id}%",),
    ).fetchall()

    # Narrow by the actual link ID (LIKE can be loose on 19-digit IDs).
    areas = []
    for r in area_rows:
        link = _parse_zoho_link(r["Staging"]) or {}
        if link.get("id") and link.get("id") != staging_id:
            continue
        raw = r["Area_Name"] or r["Area_Display_Name"] or ""
        areas.append({
            "id": r["ID"],
            "name": _strip_area_prefix(r["Area_Display_Name"] or raw) or raw,
        })

    item_rows = conn.execute(
        """
        SELECT id, area_id, action, item_name, unit_price, quantity
        FROM consultation_line_items
        WHERE staging_id = ?
        """,
        (staging_id,),
    ).fetchall()
    by_area: dict = {}
    for r in item_rows:
        lst = by_area.setdefault(r["area_id"], {"add": [], "remove": []})
        lst[r["action"]].append({
            "id": r["id"],
            "item_name": r["item_name"],
            "unit_price": r["unit_price"] or 0.0,
            "quantity": r["quantity"] or 0,
        })

    base_fee = _base_fee_for_size(property_size)
    area_payload = []
    grand_total = base_fee
    for a in areas:
        lists = by_area.get(a["id"]) or {"add": [], "remove": []}
        add_items = sorted(lists["add"], key=lambda x: x["item_name"])
        remove_items = sorted(lists["remove"], key=lambda x: x["item_name"])
        items_total = sum((i["unit_price"] or 0) * (i["quantity"] or 0) for i in add_items)
        key = _area_key_from_name(a["name"])
        cap = _area_cap(key, property_type, property_size)
        effective = min(items_total, cap) if items_total > 0 else cap
        grand_total += effective
        area_payload.append({
            "area_id": a["id"],
            "area_name": a["name"],
            "area_key": key,
            "add_items": add_items,
            "remove_items": remove_items,
            "items_total": round(items_total, 2),
            "cap": cap,
            "effective": round(effective, 2),
        })

    return {
        "staging_id": staging_id,
        "property_type": property_type or None,
        "property_size": property_size,
        "base_fee": base_fee,
        "areas": area_payload,
        "grand_total": round(grand_total, 2),
    }


# ---------------- auth helpers ----------------

def _bearer_token(request: Request):
    auth = request.headers.get("authorization", "") or request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    return auth[7:].strip() or None


def _api_user(request: Request):
    token = _bearer_token(request)
    if not token:
        return None
    return employees_db.get_user_by_session(token)


def _public_user(user: dict) -> dict:
    return {
        "id": user.get("id"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "user_role": user.get("user_role"),
    }


# ---------------- Zoho value parsers ----------------

def _parse_zoho_date(s: str):
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date().isoformat()
    except Exception:
        return None


def _parse_zoho_people(s: str):
    if not s or not s.strip():
        return []
    try:
        arr = json.loads(s)
        if isinstance(arr, list):
            return [{"name": p.get("display_value"), "id": p.get("ID")} for p in arr if isinstance(p, dict)]
    except Exception:
        pass
    return []


def _parse_zoho_link(s: str):
    if not s or not s.strip():
        return None
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return {"name": obj.get("display_value"), "id": obj.get("ID")}
    except Exception:
        pass
    return None


def _parse_money(s):
    if s is None or s == "":
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0


_ALLOWED_MILESTONE_FIELDS = {
    "Design_Items_Matched_Date",
    "Before_Picture_Upload_Date",
    "After_Picture_Upload_Date",
    "Staging_Accessories_Packing_Finish_Date",
    "Staging_Furniture_Design_Finish_Date",
    "WhatsApp_Group_Created_Date",
    "Check_Basement_Furniture_Size_Date",
}


# SELECT list shared by task_board and consultation endpoints so both deliver the
# same Staging JSON shape (keeps iOS/Android models single-source).
_STAGING_SELECT = """
    SELECT ID, Staging_Display_Name, Staging_Date, Destaging_Date,
           Staging_Address, Occupancy_Type, Property_Type, Staging_Type, Staging_Status,
           Customer_First_Name, Customer_Last_Name, Customer_Phone, Customer_Email,
           Stager, Staging_Movers, Destaging_Movers,
           Total_Staging_Fee, Owing_Amount, Paid_Amount,
           Staging_ETA, Destaging_ETA, Driving_Time,
           Before_Picture_Upload_Date, After_Picture_Upload_Date,
           Design_Items_Matched_Date, Staging_Furniture_Design_Finish_Date,
           Staging_Accessories_Packing_Finish_Date, WhatsApp_Group_Created_Date,
           Staging_Moving_Instructions, Destaging_Moving_Instructions, General_Notes,
           MLS, Pictures_Folder, HouseSigma_URL, Total_Item_Number
    FROM Staging_Report
"""


def _staging_row_to_dict(r) -> dict:
    """Map a Staging_Report row (columns from _STAGING_SELECT) to the API shape."""
    staging_date = _parse_zoho_date(r["Staging_Date"])
    destaging_date = _parse_zoho_date(r["Destaging_Date"])
    address = _parse_zoho_link(r["Staging_Address"]) or {}
    addr_text = address.get("name") or r["Staging_Display_Name"]

    def milestone(done_date_str):
        d = _parse_zoho_date(done_date_str)
        return {"done": d is not None, "date": d}

    return {
        "id": r["ID"],
        "name": r["Staging_Display_Name"],
        "staging_date": staging_date,
        "destaging_date": destaging_date,
        "address": addr_text,
        "occupancy": r["Occupancy_Type"] or None,
        "property_type": r["Property_Type"] or None,
        "staging_type": r["Staging_Type"] or None,
        "status": r["Staging_Status"] or None,
        "customer": {
            "first_name": r["Customer_First_Name"] or "",
            "last_name": r["Customer_Last_Name"] or "",
            "phone": r["Customer_Phone"] or None,
            "email": r["Customer_Email"] or None,
        },
        "stagers": _parse_zoho_people(r["Stager"]),
        "staging_movers": _parse_zoho_people(r["Staging_Movers"]),
        "destaging_movers": _parse_zoho_people(r["Destaging_Movers"]),
        "staging_eta": r["Staging_ETA"] or None,
        "destaging_eta": r["Destaging_ETA"] or None,
        "driving_time": r["Driving_Time"] or None,
        "fees": {
            "total": _parse_money(r["Total_Staging_Fee"]),
            "owing": _parse_money(r["Owing_Amount"]),
            "paid": _parse_money(r["Paid_Amount"]),
        },
        "milestones": {
            "design": milestone(r["Design_Items_Matched_Date"]),
            "before_pictures": milestone(r["Before_Picture_Upload_Date"]),
            "after_pictures": milestone(r["After_Picture_Upload_Date"]),
            "packing": milestone(r["Staging_Accessories_Packing_Finish_Date"]),
            "setup": milestone(r["Staging_Furniture_Design_Finish_Date"]),
            "whatsapp": milestone(r["WhatsApp_Group_Created_Date"]),
        },
        "moving_instructions": r["Staging_Moving_Instructions"] or None,
        "destaging_instructions": r["Destaging_Moving_Instructions"] or None,
        "general_notes": r["General_Notes"] or None,
        "mls": r["MLS"] or None,
        "pictures_folder": r["Pictures_Folder"] or None,
        "housesigma_url": r["HouseSigma_URL"] or None,
        "item_count": r["Total_Item_Number"] or 0,
    }


# ---------------- route registration ----------------

def register(rt):
    """Attach all /api/v1/* handlers to the given FastHTML router."""

    @rt("/api/v1/hello")
    def hello_v1():
        return JSONResponse({
            "message": "Hello from as_webapp (portal API)",
            "server_time": datetime.utcnow().isoformat() + "Z",
        })

    @rt("/api/v1/auth/login", methods=["POST"])
    async def v1_login(request: Request):
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        if not email or not password:
            return JSONResponse({"error": "Email and password required"}, status_code=400)

        result = employees_db.authenticate_user(email, password)
        if not result.get("success"):
            return JSONResponse({"error": result.get("error", "Authentication failed")}, status_code=401)

        user = result["user"]
        token = employees_db.create_session(user["id"])
        return JSONResponse({"token": token, "user": _public_user(user)})

    @rt("/api/v1/auth/me")
    def v1_me(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        return JSONResponse({"user": _public_user(user)})

    @rt("/api/v1/auth/logout", methods=["POST"])
    def v1_logout(request: Request):
        token = _bearer_token(request)
        if token:
            employees_db.delete_session(token)
        return JSONResponse({"success": True})

    @rt("/api/v1/tasks/board")
    def v1_tasks_board(request: Request, period: str = "upcoming", mine: str = "false"):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        today = date.today()

        def fmt(d):
            return d.strftime("%m/%d/%Y")

        sql_iso = ("substr(Staging_Date, 7, 4) || '-' || "
                   "substr(Staging_Date, 1, 2) || '-' || substr(Staging_Date, 4, 2)")

        date_filter_sql = ""
        date_params = []
        if period == "today":
            date_filter_sql = " AND (Staging_Date = ? OR Destaging_Date = ?)"
            date_params = [fmt(today), fmt(today)]
        elif period == "week":
            end = today + timedelta(days=6)
            date_filter_sql = f" AND Staging_Date != '' AND {sql_iso} BETWEEN ? AND ?"
            date_params = [today.isoformat(), end.isoformat()]
        elif period == "upcoming":
            end = today + timedelta(days=60)
            date_filter_sql = f" AND Staging_Date != '' AND {sql_iso} BETWEEN ? AND ?"
            date_params = [today.isoformat(), end.isoformat()]
        elif period == "past":
            date_filter_sql = f" AND Staging_Date != '' AND {sql_iso} < ?"
            date_params = [today.isoformat()]
        elif period == "all":
            date_filter_sql = ""
        else:
            return JSONResponse({"error": f"Invalid period: {period}"}, status_code=400)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            iso_expr = ("substr(Staging_Date, 7, 4) || '-' || "
                        "substr(Staging_Date, 1, 2) || '-' || substr(Staging_Date, 4, 2)")
            order_dir = "ASC" if period in ("today", "week", "upcoming") else "DESC"
            query = f"""
                {_STAGING_SELECT}
                WHERE _sync_status != 'deleted'
                {date_filter_sql}
                ORDER BY
                  CASE WHEN Staging_Date IS NULL OR Staging_Date = '' THEN 1 ELSE 0 END,
                  {iso_expr} {order_dir},
                  CAST(ID AS INTEGER) DESC
                LIMIT 500
            """
            rows = conn.execute(query, date_params).fetchall()
        finally:
            conn.close()

        mine_flag = mine.lower() in ("true", "1", "yes")
        first_name_lower = (user.get("first_name") or "").lower()

        out = []
        for r in rows:
            staging_date = _parse_zoho_date(r["Staging_Date"])

            if period == "week":
                if not staging_date:
                    continue
                sd = date.fromisoformat(staging_date)
                if not (today <= sd <= today + timedelta(days=6)):
                    continue
            elif period == "upcoming":
                if not staging_date:
                    continue
                sd = date.fromisoformat(staging_date)
                if sd < today or sd > today + timedelta(days=60):
                    continue
            elif period == "past":
                if not staging_date:
                    continue
                sd = date.fromisoformat(staging_date)
                if sd >= today:
                    continue

            staging = _staging_row_to_dict(r)

            if mine_flag and first_name_lower:
                assigned = staging["stagers"] + staging["staging_movers"] + staging["destaging_movers"]
                assigned_names = {p["name"].lower() for p in assigned if p.get("name")}
                if first_name_lower not in assigned_names:
                    continue

            out.append(staging)

        if period in ("upcoming", "today", "week"):
            out.sort(key=lambda s: s["staging_date"] or "9999-12-31")

        return JSONResponse({"stagings": out, "total": len(out), "period": period, "today": today.isoformat()})

    @rt("/api/v1/stagings/{staging_id}/milestone", methods=["POST"])
    async def v1_set_milestone(request: Request, staging_id: str):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        field = body.get("field")
        done = bool(body.get("done"))

        if field not in _ALLOWED_MILESTONE_FIELDS:
            return JSONResponse({"error": f"Field not allowed: {field}"}, status_code=400)

        new_value = date.today().strftime("%m/%d/%Y") if done else ""

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                f"SELECT ID, {field} AS current FROM Staging_Report WHERE ID = ?",
                (staging_id,),
            ).fetchone()
            if not row:
                return JSONResponse({"error": "Staging not found"}, status_code=404)

            old_value = row["current"] or ""
            if old_value == new_value:
                return JSONResponse({
                    "ok": True, "staging_id": staging_id, "field": field,
                    "value": new_value, "queued": False,
                })

            conn.execute(
                f"UPDATE Staging_Report SET {field} = ? WHERE ID = ?",
                (new_value, staging_id),
            )
            # Queue for Zoho push — drainer in main.py (or as_webapp in Phase 3) drains this table.
            conn.execute(
                """
                INSERT INTO pending_zoho_updates
                    (record_id, report_name, field_name, new_value, old_value)
                VALUES (?, ?, ?, ?, ?)
                """,
                (staging_id, "Staging_Report", field, new_value, old_value),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({
            "ok": True, "staging_id": staging_id, "field": field,
            "value": new_value, "queued": True,
        })

    @rt("/api/v1/stagings/consultation")
    def v1_stagings_consultation(request: Request):
        """Stagings available for a consultation: no staging date yet, or staging
        date is today or in the future. Used by the Consultation tab on mobile."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        today = date.today()
        today_iso = today.isoformat()

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            iso_expr = ("substr(Staging_Date, 7, 4) || '-' || "
                        "substr(Staging_Date, 1, 2) || '-' || substr(Staging_Date, 4, 2)")
            # Exclude 'Inactive' stagings — thousands of old cancelled leads match
            # the date filter otherwise and drown the picker. Keep Active, Inquired,
            # and anything with a null/empty status.
            query = f"""
                {_STAGING_SELECT}
                WHERE _sync_status != 'deleted'
                  AND (Staging_Status IS NULL OR Staging_Status = '' OR Staging_Status != 'Inactive')
                  AND (Staging_Date IS NULL OR Staging_Date = '' OR {iso_expr} >= ?)
                ORDER BY
                  CASE WHEN Staging_Date IS NULL OR Staging_Date = '' THEN 0 ELSE 1 END,
                  {iso_expr} ASC,
                  CAST(ID AS INTEGER) DESC
                LIMIT 500
            """
            rows = conn.execute(query, [today_iso]).fetchall()
        finally:
            conn.close()

        out = []
        for r in rows:
            # Guard against malformed dates slipping past the SQL filter.
            sd_iso = _parse_zoho_date(r["Staging_Date"])
            if sd_iso:
                try:
                    if date.fromisoformat(sd_iso) < today:
                        continue
                except ValueError:
                    pass
            out.append(_staging_row_to_dict(r))

        return JSONResponse({"stagings": out, "total": len(out), "today": today_iso})

    @rt("/api/v1/areas/catalog")
    def v1_areas_catalog(request: Request):
        """Curated list the staging team uses on-site — returned in their
        preferred order. `count` is always 0; we keep the field for client
        back-compat. Clients should show the names in list order.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        # Ordered list — identical to the Zoho Area_Name options sans NN
        # prefix. First entry ("New Area") is a placeholder stagers use when
        # the area category doesn't fit any of the standard names.
        fixed_catalog = [
            "New Area", "Living Room", "Dining Room", "Family Room",
            "Breakfast Area", "Kitchen",
            "Bedroom King", "Bedroom Queen", "Bedroom Double", "Bedroom Single",
            "Home Office", "Bathroom", "Stairs Area", "Hallway",
            "Walk-In Closet", "Laundry Room", "Patio",
            "Basement Living", "Basement Dining", "Basement Kitchen",
            "Basement Bedroom",
        ]

        catalog = [{"name": name, "count": 0} for name in fixed_catalog]
        return JSONResponse({"catalog": catalog, "total": len(catalog)})

    @rt("/api/v1/stagings/{staging_id}/areas", methods=["POST"])
    async def v1_staging_areas_create(request: Request, staging_id: str):
        """Create a new Area_Report row linked to this staging. Body:
        `{"name": "Living Room", "floor": "2nd"}`. Stored locally with
        `_sync_status = 'local_pending'` — a later sync/Zoho-push drainer
        can reconcile these into Zoho's Area form.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        name = (body.get("name") or "").strip()
        if not name:
            return JSONResponse({"error": "name is required"}, status_code=400)
        floor = (body.get("floor") or "").strip() or None

        # Assign a next NN prefix so the new area sorts after existing ones.
        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            existing = conn.execute(
                """
                SELECT Area_Name FROM Area_Report
                WHERE _sync_status != 'deleted' AND Staging LIKE ?
                """,
                (f"%{staging_id}%",),
            ).fetchall()

            valid_prefixes = []
            existing_display_names = set()
            for e in existing:
                raw = (e["Area_Name"] or "").strip()
                m = re.match(r"^(\d{1,3})\s+", raw)
                if m:
                    valid_prefixes.append(int(m.group(1)))
                display = _strip_area_prefix(raw)
                if display:
                    existing_display_names.add(display.lower())
            next_prefix = (max(valid_prefixes) + 1) if valid_prefixes else 1

            # Dedup duplicate user-visible names by appending " 2", " 3", …
            # This is independent of the NN ordering prefix — two distinct
            # areas can be "Kitchen" + "Kitchen 2" while still carrying
            # their own "01 …" / "02 …" sort prefixes.
            if name.lower() in existing_display_names:
                suffix = 2
                while f"{name} {suffix}".lower() in existing_display_names:
                    suffix += 1
                name = f"{name} {suffix}"

            prefixed = f"{next_prefix:02d} {name}"

            # Staging link field stores the same JSON shape Zoho returns.
            staging_link = json.dumps({
                "display_value": "",  # address unknown here; sync can fill
                "ID": staging_id,
            })

            # Synthesize an ID distinct from Zoho's 19-digit numeric IDs so
            # future sync drainers can find+push locally-created rows.
            new_id = f"local-{uuid.uuid4().hex}"
            added_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")

            conn.execute(
                """
                INSERT INTO Area_Report
                    (ID, Area_Name, Area_Display_Name, Floor, Staging,
                     Added_User, Added_Time, Delete_Area,
                     _modified_time, _sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'false', ?, 'local_pending')
                """,
                (
                    new_id, prefixed, prefixed, floor, staging_link,
                    user.get("email") or "", added_time,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({
            "ok": True,
            "area": {
                "id": new_id,
                "name": name,
                "raw_name": prefixed,
                "floor": floor,
                "notes": None,
            },
        })

    @rt("/api/v1/stagings/{staging_id}/areas/{area_id}", methods=["DELETE"])
    async def v1_staging_areas_delete(request: Request, staging_id: str, area_id: str):
        """Soft-delete an Area_Report row. Captures already linked to the
        area keep their area_id; clients should fall back to "Unassigned"
        in the UI. The row is tombstoned (_sync_status = 'deleted') so the
        Zoho push drainer can propagate the delete."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        try:
            cur = conn.execute(
                "UPDATE Area_Report SET _sync_status = 'deleted', "
                "Delete_Area = 'true', _modified_time = ? WHERE ID = ?",
                (datetime.utcnow().isoformat(), area_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return JSONResponse({"error": "Area not found"}, status_code=404)
        finally:
            conn.close()
        return JSONResponse({"ok": True, "staging_id": staging_id, "area_id": area_id})

    @rt("/api/v1/stagings/{staging_id}/areas/{area_id}/rename", methods=["POST"])
    async def v1_staging_areas_rename(request: Request, staging_id: str, area_id: str):
        """Rename a single Area_Report row. Used by the mobile camera when
        auto-numbering duplicate "New Area" entries (first → "New Area 1",
        second → "New Area 2", etc.). Updates both Area_Name (with its NN
        prefix preserved) and Area_Display_Name.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        new_name = (body.get("name") or "").strip()
        if not new_name:
            return JSONResponse({"error": "name is required"}, status_code=400)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT ID, Area_Name, Area_Display_Name, Floor, Staging "
                "FROM Area_Report WHERE ID = ?",
                (area_id,),
            ).fetchone()
            if not row:
                return JSONResponse({"error": "Area not found"}, status_code=404)

            # Preserve the ordering prefix if present (so the sort order on
            # the mobile picker doesn't reshuffle after a rename).
            prefix_match = re.match(r"^(\s*\d{1,3}\s+)", row["Area_Name"] or "")
            prefix = prefix_match.group(1) if prefix_match else ""
            prefixed = f"{prefix}{new_name}" if prefix else new_name

            conn.execute(
                "UPDATE Area_Report "
                "SET Area_Name = ?, Area_Display_Name = ?, _modified_time = ? "
                "WHERE ID = ?",
                (prefixed, prefixed, datetime.utcnow().isoformat(), area_id),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({
            "ok": True,
            "area": {
                "id": area_id,
                "name": new_name,
                "raw_name": prefixed,
                "floor": row["Floor"] or None,
                "notes": None,
            },
        })

    @rt("/api/v1/stagings/{staging_id}/areas")
    def v1_staging_areas(request: Request, staging_id: str):
        """Areas defined for a staging in Area_Report. The mobile Consultation
        tab uses this to group captured photos/videos by area.

        Sorted by the Zoho-supplied NN prefix (preserves stager order); the
        prefix is stripped from the returned display name.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT ID, Area_Name, Area_Display_Name, Floor, Notes, Staging,
                       Videos_and_Pictures, Added_Time
                FROM Area_Report
                WHERE _sync_status != 'deleted'
                  AND (Delete_Area IS NULL OR Delete_Area = '' OR Delete_Area = 'false')
                  AND Staging LIKE ?
                """,
                (f"%{staging_id}%",),
            ).fetchall()
        finally:
            conn.close()

        areas = []
        for r in rows:
            link = _parse_zoho_link(r["Staging"]) or {}
            # Guard against LIKE false positives — only keep rows whose parsed
            # Staging link ID matches the requested staging.
            if link.get("id") != staging_id:
                continue
            raw_name = r["Area_Name"] or r["Area_Display_Name"] or ""
            display_name = _strip_area_prefix(r["Area_Display_Name"] or raw_name) or raw_name
            areas.append({
                "id": r["ID"],
                "name": display_name or "(unnamed)",
                "raw_name": raw_name,
                "floor": r["Floor"] or None,
                "notes": r["Notes"] or None,
                "sort_key": raw_name,
            })

        areas.sort(key=lambda a: (a["sort_key"] or "").lower())
        for a in areas:
            a.pop("sort_key", None)

        return JSONResponse({
            "staging_id": staging_id,
            "areas": areas,
            "total": len(areas),
        })

    @rt("/api/v1/quote/catalog")
    def v1_quote_catalog(request: Request):
        """Item catalog (name + unit price) used by the consultation picker.
        Source-of-truth mirrors page/staging_inquiry.py."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        return JSONResponse({
            "items": [{"name": n, "unit_price": p} for n, p in _QUOTE_CATALOG],
            "total": len(_QUOTE_CATALOG),
        })

    @rt("/api/v1/stagings/{staging_id}/quote")
    def v1_staging_quote(request: Request, staging_id: str):
        """Live per-area + grand total for a staging."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            return JSONResponse(_compute_staging_quote(conn, staging_id))
        finally:
            conn.close()

    @rt("/api/v1/stagings/{staging_id}/areas/{area_id}/line-items", methods=["POST"])
    async def v1_line_items_upsert(request: Request, staging_id: str, area_id: str):
        """Tap once → quantity +1 (or –1 if `delta` = –1). If quantity hits
        0 the row is deleted. Returns the full recomputed quote so the UI
        updates in one round-trip.

        Body: `{"action": "add"|"remove", "item_name": "Sofa", "delta": 1}`
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        action = (body.get("action") or "").strip().lower()
        if action not in ("add", "remove"):
            return JSONResponse({"error": "action must be 'add' or 'remove'"}, status_code=400)
        item_name = (body.get("item_name") or "").strip()
        if not item_name:
            return JSONResponse({"error": "item_name is required"}, status_code=400)
        try:
            delta = int(body.get("delta", 1))
        except (TypeError, ValueError):
            delta = 1
        if delta == 0:
            delta = 1

        # 'add' items must be in the catalog so we always know the price.
        # 'remove' items accept anything — they don't affect the quote.
        unit_price = 0.0
        if action == "add":
            if item_name not in _QUOTE_CATALOG_MAP:
                return JSONResponse({"error": f"Unknown item: {item_name}"}, status_code=400)
            unit_price = float(_QUOTE_CATALOG_MAP[item_name])

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            existing = conn.execute(
                """
                SELECT id, quantity FROM consultation_line_items
                WHERE staging_id = ? AND area_id = ? AND action = ? AND item_name = ?
                """,
                (staging_id, area_id, action, item_name),
            ).fetchone()

            if existing:
                new_qty = (existing["quantity"] or 0) + delta
                if new_qty <= 0:
                    conn.execute(
                        "DELETE FROM consultation_line_items WHERE id = ?",
                        (existing["id"],),
                    )
                else:
                    conn.execute(
                        """
                        UPDATE consultation_line_items
                        SET quantity = ?, unit_price = ?,
                            updated_by = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (
                            new_qty, unit_price,
                            user.get("email") or "",
                            datetime.utcnow().isoformat(),
                            existing["id"],
                        ),
                    )
            else:
                if delta <= 0:
                    # Nothing to decrement — no-op but still return the quote.
                    pass
                else:
                    conn.execute(
                        """
                        INSERT INTO consultation_line_items
                            (id, staging_id, area_id, action, item_name,
                             unit_price, quantity, updated_by, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            f"li-{uuid.uuid4().hex}", staging_id, area_id, action,
                            item_name, unit_price, delta,
                            user.get("email") or "",
                            datetime.utcnow().isoformat(),
                        ),
                    )
            conn.commit()
            return JSONResponse(_compute_staging_quote(conn, staging_id))
        finally:
            conn.close()

    @rt("/api/v1/stagings/{staging_id}/areas/{area_id}/line-items/{line_id}", methods=["DELETE"])
    async def v1_line_items_delete(
        request: Request, staging_id: str, area_id: str, line_id: str,
    ):
        """Remove a single line item by id (used by the mobile trash
        icon on a picked item). Returns the refreshed quote."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(
                "DELETE FROM consultation_line_items WHERE id = ?",
                (line_id,),
            )
            conn.commit()
            return JSONResponse(_compute_staging_quote(conn, staging_id))
        finally:
            conn.close()

    @rt("/api/v1/stagings/{staging_id}/media", methods=["GET"])
    def v1_staging_media_list(request: Request, staging_id: str):
        """List previously uploaded media for this staging — grouped client-side.

        Note: `methods=["GET"]` is explicit because FastHTML registers
        routes with no-method as any-method, which was catching the POST
        upload and returning this list shape instead.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT id, staging_id, area_id, area_name, media_type, client_id,
                       file_size, mime_type, uploaded_by, uploaded_at, zoho_synced, notes
                FROM media_uploads
                WHERE staging_id = ?
                ORDER BY uploaded_at DESC
                """,
                (staging_id,),
            ).fetchall()
        finally:
            conn.close()

        out = []
        for r in rows:
            out.append({
                "id": r["id"],
                "staging_id": r["staging_id"],
                "area_id": r["area_id"],
                "area_name": r["area_name"],
                "media_type": r["media_type"],
                "client_id": r["client_id"],
                "file_size": r["file_size"],
                "mime_type": r["mime_type"],
                "uploaded_by": r["uploaded_by"],
                "uploaded_at": r["uploaded_at"],
                "zoho_synced": bool(r["zoho_synced"]),
                "notes": r["notes"],
                "url": f"/api/v1/media/{r['id']}",
            })

        return JSONResponse({
            "staging_id": staging_id,
            "media": out,
            "total": len(out),
        })

    @rt("/api/v1/stagings/{staging_id}/media", methods=["POST"])
    async def v1_staging_media_upload(request: Request, staging_id: str):
        """Receive a photo/video captured on mobile. Multipart form fields:

        - `file`: the media file (required)
        - `area_id`: Area_Report.ID (optional but recommended)
        - `area_name`: display name (optional — server falls back to DB lookup)
        - `media_type`: one of `photo`, `panorama`, `video`
        - `client_id`: UUID generated on the device — used for idempotent upload
          retries (same client_id returns the existing row).
        - `notes`: freeform (optional)
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        form = await request.form()
        upload = form.get("file")
        if upload is None or not hasattr(upload, "read"):
            return JSONResponse({"error": "Missing file field"}, status_code=400)

        media_type = (form.get("media_type") or "photo").lower()
        if media_type not in ("photo", "panorama", "video"):
            return JSONResponse({"error": "media_type must be photo|panorama|video"}, status_code=400)

        area_id = (form.get("area_id") or "").strip() or None
        area_name = (form.get("area_name") or "").strip() or None
        client_id = (form.get("client_id") or "").strip() or None
        notes = (form.get("notes") or "").strip() or None

        # Idempotent retries — device resends the same client_id on flaky links.
        if client_id:
            conn = sqlite3.connect(ZOHO_DB_PATH)
            conn.row_factory = sqlite3.Row
            try:
                existing = conn.execute(
                    "SELECT id, staging_id, area_id, area_name, media_type, file_size "
                    "FROM media_uploads WHERE client_id = ?",
                    (client_id,),
                ).fetchone()
            finally:
                conn.close()
            if existing and existing["staging_id"] == staging_id:
                return JSONResponse({
                    "ok": True,
                    "deduped": True,
                    "media": {
                        "id": existing["id"],
                        "staging_id": existing["staging_id"],
                        "area_id": existing["area_id"],
                        "area_name": existing["area_name"],
                        "media_type": existing["media_type"],
                        "file_size": existing["file_size"],
                        "url": f"/api/v1/media/{existing['id']}",
                    },
                })

        # Pick a sane extension from the uploaded filename / content type.
        original_name = getattr(upload, "filename", None) or ""
        content_type = getattr(upload, "content_type", None) or ""
        ext = os.path.splitext(original_name)[1].lower()
        if not ext:
            ext = mimetypes.guess_extension(content_type) or (".mp4" if media_type == "video" else ".jpg")
        # Normalise a few guesses.
        if ext == ".jpe":
            ext = ".jpg"

        media_id = uuid.uuid4().hex
        safe_area = (area_id or "unassigned").replace("/", "_").replace("..", "_")
        area_dir = os.path.join(MEDIA_ROOT, staging_id, safe_area)
        os.makedirs(area_dir, exist_ok=True)
        file_path = os.path.join(area_dir, f"{media_id}{ext}")

        # Write the file to disk. Starlette's UploadFile exposes an async read()
        # that returns bytes; this fits in memory because the mobile client is
        # already downscaling images and encoding 720p video.
        blob = await upload.read()
        with open(file_path, "wb") as fh:
            fh.write(blob)
        file_size = len(blob)
        mime_type = content_type or mimetypes.guess_type(file_path)[0] or None

        rel_path = os.path.relpath(file_path, ROOT)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        try:
            conn.execute(
                """
                INSERT INTO media_uploads
                    (id, staging_id, area_id, area_name, media_type, client_id,
                     file_path, file_size, mime_type, uploaded_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media_id, staging_id, area_id, area_name, media_type, client_id,
                    rel_path, file_size, mime_type, user.get("email"), notes,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({
            "ok": True,
            "deduped": False,
            "media": {
                "id": media_id,
                "staging_id": staging_id,
                "area_id": area_id,
                "area_name": area_name,
                "media_type": media_type,
                "file_size": file_size,
                "mime_type": mime_type,
                "url": f"/api/v1/media/{media_id}",
            },
        })

    @rt("/api/v1/media/{media_id}", methods=["GET"])
    def v1_media_get(request: Request, media_id: str):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT file_path, mime_type FROM media_uploads WHERE id = ?",
                (media_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return JSONResponse({"error": "Not found"}, status_code=404)

        # file_path is stored relative to ROOT; re-anchor and verify it still
        # lives under MEDIA_ROOT (defence in depth against path-escape bugs).
        full = os.path.normpath(os.path.join(ROOT, row["file_path"]))
        if not full.startswith(MEDIA_ROOT):
            return JSONResponse({"error": "Not found"}, status_code=404)
        if not os.path.exists(full):
            return JSONResponse({"error": "File missing"}, status_code=410)
        return FileResponse(full, media_type=row["mime_type"] or "application/octet-stream")

    @rt("/api/v1/media/{media_id}", methods=["DELETE"])
    def v1_media_delete(request: Request, media_id: str):
        """Delete a media row + its binary file. Fully self-contained on
        m4 — nothing propagates to Zoho."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT file_path FROM media_uploads WHERE id = ?",
                (media_id,),
            ).fetchone()
            if not row:
                return JSONResponse({"error": "Not found"}, status_code=404)

            full = os.path.normpath(os.path.join(ROOT, row["file_path"]))
            if full.startswith(MEDIA_ROOT) and os.path.exists(full):
                try:
                    os.remove(full)
                except OSError:
                    pass
            conn.execute("DELETE FROM media_uploads WHERE id = ?", (media_id,))
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({"ok": True, "media_id": media_id})

    # ---------------- Consultation Dictate ----------------
    # Mobile records AAC-LC mono 16 kHz 32 kbps .m4a, uploads here. Server
    # transcribes via Whisper, summarizes via gpt-4o-mini, stores both, and
    # returns the full record. Clients can re-fetch later to resend emails
    # without re-uploading.

    def _dictation_row_to_dict(r) -> dict:
        try:
            summary = json.loads(r["summary_json"]) if r["summary_json"] else None
        except Exception:
            summary = None
        try:
            sent = json.loads(r["sent_emails_json"]) if r["sent_emails_json"] else []
        except Exception:
            sent = []
        return {
            "id": r["id"],
            "staging_id": r["staging_id"],
            "area_id": r["area_id"],
            "area_name": r["area_name"],
            "client_id": r["client_id"],
            "audio_size": r["audio_size"],
            "duration_sec": r["duration_sec"],
            "transcript": r["transcript"] or "",
            "summary": summary,
            "status": r["status"] or "processing",
            "error": r["error"],
            "sent_emails": sent,
            "uploaded_by": r["uploaded_by"],
            "created_at": r["created_at"],
            "audio_url": f"/api/v1/dictations/{r['id']}/audio",
        }

    def _load_staging_context(staging_id: str):
        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                f"{_STAGING_SELECT} WHERE ID = ?",
                (staging_id,),
            ).fetchone()
        finally:
            conn.close()
        return _staging_row_to_dict(row) if row else None

    @rt("/api/v1/stagings/{staging_id}/dictations", methods=["POST"])
    async def v1_dictation_upload(request: Request, staging_id: str):
        """Receive a dictation audio file, transcribe + summarize, persist, return.

        Multipart form fields:
        - `file`: the audio file (required) — AAC .m4a recommended
        - `area_id`: optional Area_Report.ID
        - `area_name`: optional display name (falls back to DB)
        - `client_id`: UUID for idempotent retries
        - `duration_sec`: float, recorded on device (optional; display only)
        """
        import asyncio
        from . import ai_service

        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        form = await request.form()
        upload = form.get("file")
        if upload is None or not hasattr(upload, "read"):
            return JSONResponse({"error": "Missing file field"}, status_code=400)

        area_id = (form.get("area_id") or "").strip() or None
        area_name = (form.get("area_name") or "").strip() or None
        client_id = (form.get("client_id") or "").strip() or None
        try:
            duration_sec = float(form.get("duration_sec") or 0) or None
        except (TypeError, ValueError):
            duration_sec = None

        # Idempotent retries — same client_id returns the existing row.
        if client_id:
            conn = sqlite3.connect(ZOHO_DB_PATH)
            conn.row_factory = sqlite3.Row
            try:
                existing = conn.execute(
                    "SELECT * FROM consultation_dictations WHERE client_id = ?",
                    (client_id,),
                ).fetchone()
            finally:
                conn.close()
            if existing and existing["staging_id"] == staging_id:
                return JSONResponse({
                    "ok": True,
                    "deduped": True,
                    "dictation": _dictation_row_to_dict(existing),
                })

        # Persist the audio file under data/staging_media/<staging>/dictations/.
        original_name = getattr(upload, "filename", None) or ""
        content_type = getattr(upload, "content_type", None) or "audio/m4a"
        ext = os.path.splitext(original_name)[1].lower() or ".m4a"

        dictation_id = uuid.uuid4().hex
        area_dir = os.path.join(MEDIA_ROOT, staging_id, "dictations")
        os.makedirs(area_dir, exist_ok=True)
        audio_path = os.path.join(area_dir, f"{dictation_id}{ext}")

        blob = await upload.read()
        with open(audio_path, "wb") as fh:
            fh.write(blob)
        audio_size = len(blob)
        rel_path = os.path.relpath(audio_path, ROOT)

        # Insert row first in `processing` state so the client can poll /GET
        # if we ever move to async processing. For now we run transcribe+summary
        # inline on the request thread (worst case ~60s for a 1-hour audio).
        conn = sqlite3.connect(ZOHO_DB_PATH)
        try:
            conn.execute(
                """
                INSERT INTO consultation_dictations
                    (id, staging_id, area_id, area_name, client_id,
                     audio_path, audio_size, duration_sec, status, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'processing', ?)
                """,
                (
                    dictation_id, staging_id, area_id, area_name, client_id,
                    rel_path, audio_size, duration_sec, user.get("email"),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        transcript = ""
        summary = None
        status = "processing"
        error_msg = None
        try:
            transcript = await asyncio.to_thread(
                ai_service.transcribe_audio, audio_path
            )
        except ai_service.AIServiceError as exc:
            error_msg = f"transcription failed: {exc}"
            status = "error"

        if status != "error":
            try:
                staging_ctx = _load_staging_context(staging_id)
                summary = await asyncio.to_thread(
                    ai_service.summarize_consultation,
                    transcript, staging_ctx, area_name,
                )
                status = "ready"
            except ai_service.AIServiceError as exc:
                error_msg = f"summary failed: {exc}"
                status = "transcribed"  # still useful — transcript is saved

        conn = sqlite3.connect(ZOHO_DB_PATH)
        try:
            conn.execute(
                """
                UPDATE consultation_dictations
                   SET transcript = ?, summary_json = ?, status = ?, error = ?
                 WHERE id = ?
                """,
                (
                    transcript,
                    json.dumps(summary) if summary else None,
                    status,
                    error_msg,
                    dictation_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT * FROM consultation_dictations WHERE id = ?",
                (dictation_id,),
            ).fetchone()
        finally:
            conn.close()

        http_status = 200 if status in ("ready", "transcribed") else 502
        return JSONResponse(
            {"ok": status in ("ready", "transcribed"),
             "deduped": False,
             "dictation": _dictation_row_to_dict(row)},
            status_code=http_status,
        )

    @rt("/api/v1/stagings/{staging_id}/dictations")
    def v1_dictations_list(request: Request, staging_id: str):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT * FROM consultation_dictations
                 WHERE staging_id = ?
              ORDER BY created_at DESC
                """,
                (staging_id,),
            ).fetchall()
        finally:
            conn.close()

        return JSONResponse({
            "staging_id": staging_id,
            "dictations": [_dictation_row_to_dict(r) for r in rows],
            "total": len(rows),
        })

    @rt("/api/v1/dictations/{dictation_id}", methods=["DELETE"])
    def v1_dictation_delete(request: Request, dictation_id: str):
        """Remove a dictation: deletes the audio file from disk and drops
        the row. Transcript + summary are lost with the row; email-sent
        history goes with it too."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT audio_path FROM consultation_dictations WHERE id = ?",
                (dictation_id,),
            ).fetchone()
            if not row:
                return JSONResponse({"error": "Not found"}, status_code=404)

            full = os.path.normpath(os.path.join(ROOT, row["audio_path"]))
            if full.startswith(MEDIA_ROOT) and os.path.exists(full):
                try:
                    os.remove(full)
                except OSError:
                    # File missing is fine; swallow to keep delete idempotent.
                    pass

            conn.execute(
                "DELETE FROM consultation_dictations WHERE id = ?",
                (dictation_id,),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse({"ok": True, "dictation_id": dictation_id})

    @rt("/api/v1/dictations/{dictation_id}/audio")
    def v1_dictation_audio(request: Request, dictation_id: str):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT audio_path FROM consultation_dictations WHERE id = ?",
                (dictation_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return JSONResponse({"error": "Not found"}, status_code=404)

        full = os.path.normpath(os.path.join(ROOT, row["audio_path"]))
        if not full.startswith(MEDIA_ROOT):
            return JSONResponse({"error": "Not found"}, status_code=404)
        if not os.path.exists(full):
            return JSONResponse({"error": "File missing"}, status_code=410)
        return FileResponse(full, media_type="audio/m4a")

    @rt("/api/v1/dictations/{dictation_id}/send-email", methods=["POST"])
    async def v1_dictation_send_email(request: Request, dictation_id: str):
        """Send a dictation email draft via Mailgun.

        Body (JSON):
        {
          "recipient": "customer" | "sales_rep" | "both",
          "to_customer": "optional override for the customer's email",
          "customer_subject": "optional override of the draft",
          "customer_body": "optional override",
          "sales_rep_subject": "optional override",
          "sales_rep_body": "optional override"
        }
        Falls back to the summary draft stored on the dictation when a field is
        absent. Sales-rep recipient is always sales@astrastaging.com.
        """
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        recipient = (body.get("recipient") or "").lower()
        if recipient not in ("customer", "sales_rep", "both"):
            return JSONResponse(
                {"error": "recipient must be customer|sales_rep|both"},
                status_code=400,
            )

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT * FROM consultation_dictations WHERE id = ?",
                (dictation_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return JSONResponse({"error": "Not found"}, status_code=404)

        try:
            summary = json.loads(row["summary_json"]) if row["summary_json"] else {}
        except Exception:
            summary = {}

        staging_ctx = _load_staging_context(row["staging_id"]) or {}
        default_customer_email = (staging_ctx.get("customer") or {}).get("email")

        # Import lazily so missing MAILGUN_API_KEY surfaces as a clean error at
        # call time rather than blocking module import.
        try:
            from tools.email_service import EmailService, ADMIN_EMAIL
        except Exception as exc:
            return JSONResponse(
                {"error": f"Email service unavailable: {exc}"},
                status_code=500,
            )

        mailer = EmailService()
        sent_log = []
        errors = []

        def _text_to_html(text: str) -> str:
            """Wrap plain-text draft in a minimal HTML shell so Mailgun is happy
            and long paragraphs wrap. Preserves line breaks."""
            safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return (
                "<html><body style=\"font-family:Arial,sans-serif;"
                "line-height:1.5;color:#222;\">"
                + safe.replace("\n", "<br>")
                + "</body></html>"
            )

        if recipient in ("customer", "both"):
            to_customer = (body.get("to_customer") or default_customer_email or "").strip()
            subj = (body.get("customer_subject") or summary.get("customer_email_subject") or "").strip()
            text = (body.get("customer_body") or summary.get("customer_email_body") or "").strip()
            if not to_customer:
                errors.append("customer: no email address available")
            elif not subj or not text:
                errors.append("customer: missing subject or body")
            else:
                res = mailer.send_email(
                    to_customer, subj, _text_to_html(text), text,
                    reply_to=user.get("email"),
                )
                sent_log.append({
                    "recipient": "customer",
                    "to": to_customer,
                    "subject": subj,
                    "sent_at": datetime.utcnow().isoformat() + "Z",
                    "success": bool(res.get("success")),
                    "message_id": res.get("message_id"),
                    "error": res.get("error"),
                })
                if not res.get("success"):
                    errors.append(f"customer: {res.get('error')}")

        if recipient in ("sales_rep", "both"):
            to_sales = ADMIN_EMAIL  # sales@astrastaging.com
            subj = (body.get("sales_rep_subject") or summary.get("sales_rep_email_subject") or "").strip()
            text = (body.get("sales_rep_body") or summary.get("sales_rep_email_body") or "").strip()
            if not subj or not text:
                errors.append("sales_rep: missing subject or body")
            else:
                res = mailer.send_email(
                    to_sales, subj, _text_to_html(text), text,
                    reply_to=user.get("email"),
                )
                sent_log.append({
                    "recipient": "sales_rep",
                    "to": to_sales,
                    "subject": subj,
                    "sent_at": datetime.utcnow().isoformat() + "Z",
                    "success": bool(res.get("success")),
                    "message_id": res.get("message_id"),
                    "error": res.get("error"),
                })
                if not res.get("success"):
                    errors.append(f"sales_rep: {res.get('error')}")

        # Append to the stored send history.
        try:
            prior = json.loads(row["sent_emails_json"]) if row["sent_emails_json"] else []
        except Exception:
            prior = []
        combined = prior + sent_log

        conn = sqlite3.connect(ZOHO_DB_PATH)
        try:
            conn.execute(
                "UPDATE consultation_dictations SET sent_emails_json = ? WHERE id = ?",
                (json.dumps(combined), dictation_id),
            )
            conn.commit()
        finally:
            conn.close()

        return JSONResponse(
            {
                "ok": len(errors) == 0,
                "sent": sent_log,
                "errors": errors,
            },
            status_code=200 if not errors else 207,
        )

    @rt("/api/v1/items")
    def v1_items(request: Request, search: str = "", limit: int = 100):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        conn = sqlite3.connect(ZOHO_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            query = """
                SELECT Item_Name, Item_Type, Item_Image, Resized_Image, Item_Color, Item_Style,
                       Model_3D, Item_Width, Item_Depth, Item_Height, COUNT(*) as item_count
                FROM Item_Report
                WHERE Item_Name IS NOT NULL AND Item_Name != ''
            """
            params = []
            if search:
                query += " AND (Item_Name LIKE ? OR Item_Type LIKE ?)"
                needle = f"%{search}%"
                params.extend([needle, needle])
            query += " GROUP BY Item_Name ORDER BY Item_Name LIMIT ?"
            params.append(max(1, min(limit, 500)))

            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

        def pick_image(row):
            for key in ("Resized_Image", "Item_Image"):
                val = (row[key] or "").strip()
                if val and val != "blank.png" and (val.startswith("http://") or val.startswith("https://")):
                    return val
            return None

        items = []
        for r in rows:
            items.append({
                "name": r["Item_Name"],
                "type": r["Item_Type"],
                "color": r["Item_Color"],
                "style": r["Item_Style"],
                "image_url": pick_image(r),
                "model_3d": r["Model_3D"] or None,
                "width": r["Item_Width"],
                "depth": r["Item_Depth"],
                "height": r["Item_Height"],
                "count": r["item_count"],
            })
        return JSONResponse({"items": items, "total": len(items)})
