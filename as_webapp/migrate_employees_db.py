"""
One-shot migration: create data/employees.db and seed it with employee rows
copied from data/users.db. Customer rows stay in users.db (to be renamed
customers.db in Phase 2).

An "employee" is a user with user_role in {'owner', 'manager', 'execution'}
OR a user that has a zoho_employee_id set. Anyone else is a customer.

Safe to re-run: drops and recreates employees.db from scratch each time.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "users.db"
DST = ROOT / "data" / "employees.db"

EMPLOYEE_ROLES = {"owner", "manager", "execution"}


def main():
    if DST.exists():
        DST.unlink()

    dst = sqlite3.connect(str(DST))
    dst.row_factory = sqlite3.Row
    dst.executescript(
        """
        PRAGMA journal_mode = WAL;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT,
            user_role TEXT NOT NULL DEFAULT 'execution',
            zoho_employee_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE INDEX idx_sessions_token ON sessions (session_token);
        CREATE INDEX idx_sessions_user ON sessions (user_id);
        """
    )

    if not SRC.exists():
        print(f"Source {SRC} not found — created empty employees.db. Seed manually.")
        dst.commit()
        dst.close()
        return

    src = sqlite3.connect(str(SRC))
    src.row_factory = sqlite3.Row

    users = src.execute(
        "SELECT id, first_name, last_name, email, phone, password_hash, "
        "user_role, zoho_employee_id, created_at, updated_at, last_login, is_active "
        "FROM users"
    ).fetchall()

    moved = 0
    skipped = 0
    for u in users:
        role = (u["user_role"] or "").lower()
        has_zoho_emp = bool(u["zoho_employee_id"])
        if role in EMPLOYEE_ROLES or (has_zoho_emp and role != "customer"):
            dst.execute(
                "INSERT INTO users (first_name, last_name, email, phone, password_hash, "
                "user_role, zoho_employee_id, created_at, updated_at, last_login, is_active) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    u["first_name"], u["last_name"], u["email"], u["phone"],
                    u["password_hash"], u["user_role"] or "execution",
                    u["zoho_employee_id"], u["created_at"], u["updated_at"],
                    u["last_login"], u["is_active"],
                ),
            )
            moved += 1
            print(f"  → migrated: {u['email']} ({u['user_role']})")
        else:
            skipped += 1
            print(f"  ✗ skipped (customer): {u['email']}")

    dst.commit()
    dst.close()
    src.close()
    print(f"\nDone. Migrated {moved} employee(s), skipped {skipped} customer(s).")
    print(f"employees.db at: {DST}")


if __name__ == "__main__":
    main()
