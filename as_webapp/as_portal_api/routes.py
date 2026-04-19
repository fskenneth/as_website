"""
/api/v1/* — Bearer-token API for iOS and Android clients.

Extracted from as_website/main.py during the as_webapp split. Contract is
unchanged; only the auth backend now points at data/employees.db (not
data/users.db) and writes to pending_zoho_updates via plain sqlite3
(the drainer running in main.py — or later in as_webapp — picks them up).
"""
from datetime import date, datetime, timedelta
import json
import os
import sqlite3

from starlette.requests import Request
from starlette.responses import JSONResponse

from . import employees_db

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZOHO_DB_PATH = os.path.join(ROOT, "data", "zoho_sync.db")


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
            destaging_date = _parse_zoho_date(r["Destaging_Date"])

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

            stagers = _parse_zoho_people(r["Stager"])
            staging_movers = _parse_zoho_people(r["Staging_Movers"])
            destaging_movers = _parse_zoho_people(r["Destaging_Movers"])

            if mine_flag and first_name_lower:
                assigned_names = {p["name"].lower() for p in stagers + staging_movers + destaging_movers if p.get("name")}
                if first_name_lower not in assigned_names:
                    continue

            address = _parse_zoho_link(r["Staging_Address"]) or {}
            addr_text = address.get("name") or r["Staging_Display_Name"]

            def milestone(done_date_str):
                d = _parse_zoho_date(done_date_str)
                return {"done": d is not None, "date": d}

            out.append({
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
                "stagers": stagers,
                "staging_movers": staging_movers,
                "destaging_movers": destaging_movers,
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
            })

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
