"""
Employee auth helpers for as_webapp.

Separate from tools/user_db.py (which points at data/users.db for customer
auth). This module exclusively reads/writes data/employees.db.

Mirrors the shape returned by tools.user_db so the route handlers can drop
in without contract changes: authenticate_user(email, password) returns
{'success': bool, 'user': {...}, 'error': str}.
"""
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "employees.db"
SESSION_DAYS = 30


def _conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _verify_password(password: str, stored_hash: str) -> bool:
    """Matches tools/user_db.py format: 'salt:sha256(password+salt)'."""
    if not stored_hash or ":" not in stored_hash:
        return False
    salt, hash_value = stored_hash.split(":", 1)
    candidate = hashlib.sha256((password + salt).encode()).hexdigest()
    return candidate == hash_value


def _row_to_user(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"],
        "first_name": r["first_name"],
        "last_name": r["last_name"],
        "email": r["email"],
        "phone": r["phone"],
        "user_role": r["user_role"],
        "zoho_employee_id": r["zoho_employee_id"],
        "is_active": bool(r["is_active"]),
    }


def authenticate_user(email: str, password: str) -> dict:
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email.strip().lower(),),
        ).fetchone()
        if not row:
            # fall back to exact-case lookup (legacy users like "kenneth")
            row = conn.execute(
                "SELECT * FROM users WHERE email = ? AND is_active = 1",
                (email,),
            ).fetchone()
        if not row:
            return {"success": False, "error": "Invalid credentials"}
        if not _verify_password(password, row["password_hash"] or ""):
            return {"success": False, "error": "Invalid credentials"}

        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (row["id"],),
        )
        conn.commit()
        return {"success": True, "user": _row_to_user(row)}
    finally:
        conn.close()


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(days=SESSION_DAYS)
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires.isoformat(" ")),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def get_user_by_session(token: str):
    if not token:
        return None
    conn = _conn()
    try:
        row = conn.execute(
            """
            SELECT u.* FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.session_token = ?
              AND s.expires_at > CURRENT_TIMESTAMP
              AND u.is_active = 1
            """,
            (token,),
        ).fetchone()
        return _row_to_user(row) if row else None
    finally:
        conn.close()


def delete_session(token: str) -> None:
    if not token:
        return
    conn = _conn()
    try:
        conn.execute("DELETE FROM sessions WHERE session_token = ?", (token,))
        conn.commit()
    finally:
        conn.close()
