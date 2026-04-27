"""
Chat data layer for the internal team channel.

Single SQLite file at data/chat.db. The other channels (whatsapp, sms, anna,
email) will eventually share these tables — `conversations.channel` is the
discriminator and stays present even though phase 1 only writes 'internal'.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "chat.db"
EMPLOYEES_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "employees.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema() -> None:
    """Create tables on first import. Idempotent."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _conn()
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL DEFAULT 'internal',
            kind TEXT NOT NULL DEFAULT 'dm',
            title TEXT,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_message_at TEXT,
            last_message_preview TEXT,
            last_message_sender_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS participants (
            conversation_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            joined_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_read_message_id INTEGER,
            archived_at TEXT,
            pinned_position INTEGER,
            PRIMARY KEY (conversation_id, user_id),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_participants_user ON participants(user_id);

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'text',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            edited_at TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv_time
            ON messages(conversation_id, id);

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            title TEXT,
            body TEXT,
            data_json TEXT,
            read_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(user_id, read_at, id);

        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            file_path TEXT NOT NULL,
            mime_type TEXT,
            size INTEGER,
            original_name TEXT,
            width INTEGER,
            height INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_attachments_msg ON attachments(message_id);

        CREATE TABLE IF NOT EXISTS reactions (
            message_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            emoji TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (message_id, employee_id, emoji),
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_reactions_msg ON reactions(message_id);

        CREATE TABLE IF NOT EXISTS device_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            app_version TEXT,
            last_seen TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """)
        # Idempotent column upgrades for existing installs.
        existing = {r["name"] for r in conn.execute("PRAGMA table_info(participants)").fetchall()}
        if "archived_at" not in existing:
            conn.execute("ALTER TABLE participants ADD COLUMN archived_at TEXT")
        if "pinned_position" not in existing:
            conn.execute("ALTER TABLE participants ADD COLUMN pinned_position INTEGER")
        msg_cols = {r["name"] for r in conn.execute("PRAGMA table_info(messages)").fetchall()}
        if "reply_to_message_id" not in msg_cols:
            conn.execute("ALTER TABLE messages ADD COLUMN reply_to_message_id INTEGER")
        if "deleted_at" not in msg_cols:
            conn.execute("ALTER TABLE messages ADD COLUMN deleted_at TEXT")
        conn.commit()
    finally:
        conn.close()


# How long after sending the user is allowed to edit / delete a message.
MESSAGE_MUTABLE_SECONDS = 10


def list_employees(exclude_user_id: int | None = None) -> list[dict]:
    """Pull all active employees from employees.db so the chat picker can
    show them. Cross-DB attach is the simplest path; same disk."""
    conn = _conn()
    try:
        conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
        rows = conn.execute("""
            SELECT id, first_name, last_name, email, user_role
            FROM emp.users
            WHERE is_active = 1
            ORDER BY first_name, last_name
        """).fetchall()
        out = []
        for r in rows:
            if exclude_user_id is not None and r["id"] == exclude_user_id:
                continue
            out.append({
                "id": r["id"],
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "email": r["email"],
                "user_role": r["user_role"],
                "display_name": (r["first_name"] or "").strip() or r["email"],
            })
        return out
    finally:
        conn.close()


def get_employee(user_id: int) -> dict | None:
    conn = _conn()
    try:
        conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
        r = conn.execute(
            "SELECT id, first_name, last_name, email, user_role "
            "FROM emp.users WHERE id = ? AND is_active = 1",
            (user_id,),
        ).fetchone()
        if not r:
            return None
        return {
            "id": r["id"],
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "user_role": r["user_role"],
            "display_name": (r["first_name"] or "").strip() or r["email"],
        }
    finally:
        conn.close()


def find_or_create_dm(user_a: int, user_b: int) -> dict:
    """Return the DM conversation between these two users; create if absent.
    DMs are deduplicated by participant set, not by title."""
    if user_a == user_b:
        raise ValueError("cannot DM yourself")
    a, b = sorted((user_a, user_b))
    conn = _conn()
    try:
        row = conn.execute("""
            SELECT c.id FROM conversations c
            WHERE c.kind = 'dm' AND c.channel = 'internal'
              AND EXISTS (SELECT 1 FROM participants p WHERE p.conversation_id = c.id AND p.user_id = ?)
              AND EXISTS (SELECT 1 FROM participants p WHERE p.conversation_id = c.id AND p.user_id = ?)
              AND (SELECT COUNT(*) FROM participants p WHERE p.conversation_id = c.id) = 2
            LIMIT 1
        """, (a, b)).fetchone()
        if row:
            cid = row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO conversations (channel, kind, created_by) "
                "VALUES ('internal', 'dm', ?)",
                (user_a,),
            )
            cid = cur.lastrowid
            conn.executemany(
                "INSERT INTO participants (conversation_id, user_id) VALUES (?, ?)",
                [(cid, a), (cid, b)],
            )
            conn.commit()
        return get_conversation(cid, user_a)
    finally:
        conn.close()


def create_group(creator_id: int, title: str, member_ids: list[int]) -> dict:
    members = set(member_ids) | {creator_id}
    if len(members) < 2:
        raise ValueError("group needs at least 2 members")
    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO conversations (channel, kind, title, created_by) "
            "VALUES ('internal', 'group', ?, ?)",
            (title.strip() or "Group", creator_id),
        )
        cid = cur.lastrowid
        rows = [
            (cid, uid, 'admin' if uid == creator_id else 'member')
            for uid in members
        ]
        conn.executemany(
            "INSERT INTO participants (conversation_id, user_id, role) "
            "VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
    return get_conversation(cid, creator_id)


def list_conversations(user_id: int, archived: bool = False) -> list[dict]:
    """Return conversations this user participates in. By default returns
    only unarchived rows; pass archived=True to get the archived set.

    Ordering: pinned_position ASC NULLS LAST, then last_message_at DESC.
    Anna's conversation is force-pinned to the top by chat_routes.
    """
    conn = _conn()
    try:
        conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
        archive_filter = (
            "AND p.archived_at IS NOT NULL" if archived
            else "AND p.archived_at IS NULL"
        )
        rows = conn.execute(f"""
            SELECT c.id, c.channel, c.kind, c.title, c.created_by,
                   c.created_at, c.last_message_at, c.last_message_preview,
                   c.last_message_sender_id,
                   p.last_read_message_id, p.archived_at, p.pinned_position
            FROM conversations c
            JOIN participants p ON p.conversation_id = c.id
            WHERE p.user_id = ?
              {archive_filter}
            ORDER BY
              CASE WHEN p.pinned_position IS NULL THEN 1 ELSE 0 END,
              p.pinned_position,
              COALESCE(c.last_message_at, c.created_at) DESC
        """, (user_id,)).fetchall()
        out = []
        for r in rows:
            unread = conn.execute("""
                SELECT COUNT(*) AS n FROM messages m
                WHERE m.conversation_id = ?
                  AND m.id > COALESCE(?, 0)
                  AND m.sender_id != ?
            """, (r["id"], r["last_read_message_id"], user_id)).fetchone()["n"]
            display_title = _resolve_title(conn, dict(r), user_id)
            out.append({
                "id": r["id"],
                "channel": r["channel"],
                "kind": r["kind"],
                "title": display_title,
                "created_by": r["created_by"],
                "created_at": r["created_at"],
                "last_message_at": r["last_message_at"],
                "last_message_preview": r["last_message_preview"],
                "last_message_sender_id": r["last_message_sender_id"],
                "unread_count": unread,
                "archived": r["archived_at"] is not None,
                "pinned_position": r["pinned_position"],
            })
        return out
    finally:
        conn.close()


def set_archived(conv_id: int, user_id: int, archived: bool) -> bool:
    conn = _conn()
    try:
        cur = conn.execute(
            "UPDATE participants "
            "SET archived_at = CASE WHEN ? THEN datetime('now') ELSE NULL END "
            "WHERE conversation_id = ? AND user_id = ?",
            (1 if archived else 0, conv_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def set_pinned_order(user_id: int, conv_ids_in_order: list[int]) -> int:
    """Stamp pinned_position 0..N-1 onto these conversations for the given
    user. Conversations not present in the list keep whatever they had."""
    conn = _conn()
    try:
        for idx, cid in enumerate(conv_ids_in_order):
            conn.execute(
                "UPDATE participants SET pinned_position = ? "
                "WHERE conversation_id = ? AND user_id = ?",
                (idx, cid, user_id),
            )
        conn.commit()
        return len(conv_ids_in_order)
    finally:
        conn.close()


def delete_conversation(conv_id: int) -> bool:
    """Hard-delete a conversation row (cascades to participants + messages
    via FK on participants; messages are removed by the FK on their own).
    Caller is responsible for permission checks."""
    conn = _conn()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        # Manually delete messages — sqlite's FK cascade fires only when
        # the FK definition includes ON DELETE CASCADE, which messages
        # already has but participants do not. Belt-and-braces:
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        conn.execute("DELETE FROM participants WHERE conversation_id = ?", (conv_id,))
        cur = conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def _resolve_title(conn: sqlite3.Connection, conv: dict, viewer_id: int) -> str:
    if conv["kind"] == "group":
        return conv["title"] or "Group"
    other = conn.execute("""
        SELECT u.first_name, u.last_name, u.email
        FROM participants p
        JOIN emp.users u ON u.id = p.user_id
        WHERE p.conversation_id = ? AND p.user_id != ?
        LIMIT 1
    """, (conv["id"], viewer_id)).fetchone()
    if not other:
        return conv["title"] or "Conversation"
    return (other["first_name"] or "").strip() or other["email"]


def get_conversation(conv_id: int, viewer_id: int) -> dict | None:
    conn = _conn()
    try:
        conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
        r = conn.execute("""
            SELECT c.*, p.last_read_message_id
            FROM conversations c
            JOIN participants p ON p.conversation_id = c.id
            WHERE c.id = ? AND p.user_id = ?
        """, (conv_id, viewer_id)).fetchone()
        if not r:
            return None
        members = conn.execute("""
            SELECT u.id, u.first_name, u.last_name, u.email, u.user_role,
                   p.role, p.last_read_message_id
            FROM participants p
            JOIN emp.users u ON u.id = p.user_id
            WHERE p.conversation_id = ?
            ORDER BY u.first_name
        """, (conv_id,)).fetchall()
        return {
            "id": r["id"],
            "channel": r["channel"],
            "kind": r["kind"],
            "title": _resolve_title(conn, dict(r), viewer_id),
            "created_by": r["created_by"],
            "created_at": r["created_at"],
            "last_message_at": r["last_message_at"],
            "last_message_preview": r["last_message_preview"],
            "members": [
                {
                    "id": m["id"],
                    "display_name": (m["first_name"] or "").strip() or m["email"],
                    "email": m["email"],
                    "user_role": m["user_role"],
                    "role": m["role"],
                }
                for m in members
            ],
        }
    finally:
        conn.close()


def is_participant(conv_id: int, user_id: int) -> bool:
    conn = _conn()
    try:
        r = conn.execute(
            "SELECT 1 FROM participants WHERE conversation_id = ? AND user_id = ?",
            (conv_id, user_id),
        ).fetchone()
        return r is not None
    finally:
        conn.close()


_MSG_COLS = (
    "id, conversation_id, sender_id, body, kind, created_at, "
    "edited_at, deleted_at, reply_to_message_id"
)


def _hydrate_message(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    """Turn a messages row into the API shape, including a sender display
    name, an optional `reply_to` quote preview, and aggregated `reactions`
    (one row per emoji with count + user_ids)."""
    conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
    sender = conn.execute(
        "SELECT first_name, last_name, email FROM emp.users WHERE id = ?",
        (row["sender_id"],),
    ).fetchone()
    sender_name = (sender["first_name"] or "").strip() if sender else ""
    if not sender_name and sender:
        sender_name = sender["email"]

    reply_to = None
    rid = row["reply_to_message_id"] if "reply_to_message_id" in row.keys() else None
    if rid:
        r = conn.execute(
            "SELECT id, sender_id, body, deleted_at FROM messages WHERE id = ?",
            (rid,),
        ).fetchone()
        if r:
            r_sender = conn.execute(
                "SELECT first_name, email FROM emp.users WHERE id = ?",
                (r["sender_id"],),
            ).fetchone()
            r_name = (r_sender["first_name"] or "").strip() if r_sender else ""
            if not r_name and r_sender:
                r_name = r_sender["email"]
            preview = "(message deleted)" if r["deleted_at"] else (r["body"] or "")
            reply_to = {
                "id": r["id"],
                "sender_id": r["sender_id"],
                "sender_name": r_name,
                "body": preview[:200],
                "deleted": r["deleted_at"] is not None,
            }

    # Attachments (photos/videos/files) for this message.
    att_rows = conn.execute(
        "SELECT id, kind, mime_type, size, original_name, width, height "
        "FROM attachments WHERE message_id = ? ORDER BY id",
        (row["id"],),
    ).fetchall()
    attachments = [
        {
            "id": a["id"],
            "kind": a["kind"],
            "mime_type": a["mime_type"],
            "size": a["size"],
            "original_name": a["original_name"],
            "width": a["width"],
            "height": a["height"],
            "url": f"/api/v1/chat/attachments/{a['id']}",
        }
        for a in att_rows
    ]

    # Aggregated reactions for this message.
    rxn_rows = conn.execute(
        "SELECT emoji, employee_id FROM reactions WHERE message_id = ? ORDER BY emoji",
        (row["id"],),
    ).fetchall()
    by_emoji: dict[str, list[int]] = {}
    for rr in rxn_rows:
        by_emoji.setdefault(rr["emoji"], []).append(rr["employee_id"])
    reactions = [
        {"emoji": e, "count": len(uids), "user_ids": uids}
        for e, uids in by_emoji.items()
    ]

    return {
        "id": row["id"],
        "conversation_id": row["conversation_id"],
        "sender_id": row["sender_id"],
        "body": row["body"] if not row["deleted_at"] else "",
        "kind": row["kind"],
        "created_at": row["created_at"],
        "edited_at": row["edited_at"],
        "deleted_at": row["deleted_at"],
        "deleted": row["deleted_at"] is not None,
        "reply_to": reply_to,
        "reactions": reactions,
        "attachments": attachments,
        "sender": {"id": row["sender_id"], "display_name": sender_name},
    }


# Where uploaded chat media lives. One subdir per conversation so we can
# easily nuke a conversation's media if the conversation is deleted.
CHAT_MEDIA_DIR = Path(__file__).resolve().parents[2] / "data" / "chat_media"


def insert_attachment(
    message_id: int,
    kind: str,
    file_path: str,
    mime_type: str | None = None,
    size: int | None = None,
    original_name: str | None = None,
    width: int | None = None,
    height: int | None = None,
) -> int:
    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO attachments "
            "(message_id, kind, file_path, mime_type, size, original_name, width, height) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (message_id, kind, file_path, mime_type, size, original_name, width, height),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_attachment(attachment_id: int) -> dict | None:
    conn = _conn()
    try:
        r = conn.execute(
            "SELECT a.*, m.conversation_id "
            "FROM attachments a JOIN messages m ON m.id = a.message_id "
            "WHERE a.id = ?",
            (attachment_id,),
        ).fetchone()
        return dict(r) if r else None
    finally:
        conn.close()


def toggle_reaction(msg_id: int, user_id: int, emoji: str) -> dict | None:
    """Toggle a user's reaction with this emoji on a message: insert if it
    doesn't exist, delete if it does. Returns the updated hydrated message."""
    emoji = emoji.strip()
    if not emoji or len(emoji) > 16:
        return None
    conn = _conn()
    try:
        existing = conn.execute(
            "SELECT 1 FROM reactions "
            "WHERE message_id = ? AND employee_id = ? AND emoji = ?",
            (msg_id, user_id, emoji),
        ).fetchone()
        if existing:
            conn.execute(
                "DELETE FROM reactions "
                "WHERE message_id = ? AND employee_id = ? AND emoji = ?",
                (msg_id, user_id, emoji),
            )
        else:
            # Don't allow reactions on messages that don't exist or are
            # in conversations the user isn't a participant of.
            row = conn.execute(
                "SELECT m.id, m.conversation_id FROM messages m WHERE m.id = ?",
                (msg_id,),
            ).fetchone()
            if not row:
                return None
            participates = conn.execute(
                "SELECT 1 FROM participants "
                "WHERE conversation_id = ? AND user_id = ?",
                (row["conversation_id"], user_id),
            ).fetchone()
            if not participates:
                return None
            conn.execute(
                "INSERT OR IGNORE INTO reactions (message_id, employee_id, emoji) "
                "VALUES (?, ?, ?)",
                (msg_id, user_id, emoji),
            )
        m = conn.execute(
            f"SELECT {_MSG_COLS} FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        out = _hydrate_message(conn, m) if m else None
        conn.commit()
        return out
    finally:
        conn.close()


def list_messages(conv_id: int, limit: int = 50, before_id: int | None = None) -> list[dict]:
    conn = _conn()
    try:
        if before_id:
            rows = conn.execute(f"""
                SELECT {_MSG_COLS} FROM messages
                WHERE conversation_id = ? AND id < ?
                ORDER BY id DESC LIMIT ?
            """, (conv_id, before_id, limit)).fetchall()
        else:
            rows = conn.execute(f"""
                SELECT {_MSG_COLS} FROM messages
                WHERE conversation_id = ?
                ORDER BY id DESC LIMIT ?
            """, (conv_id, limit)).fetchall()
        return [_hydrate_message(conn, r) for r in reversed(rows)]
    finally:
        conn.close()


def get_message(msg_id: int) -> dict | None:
    conn = _conn()
    try:
        r = conn.execute(
            f"SELECT {_MSG_COLS} FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        return _hydrate_message(conn, r) if r else None
    finally:
        conn.close()


def insert_message(
    conv_id: int,
    sender_id: int,
    body: str,
    kind: str = "text",
    reply_to_message_id: int | None = None,
) -> dict:
    body = body.strip()
    if not body:
        raise ValueError("empty message")
    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO messages (conversation_id, sender_id, body, kind, reply_to_message_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (conv_id, sender_id, body, kind, reply_to_message_id),
        )
        msg_id = cur.lastrowid
        preview = body[:140]
        conn.execute(
            "UPDATE conversations "
            "SET last_message_at = datetime('now'), "
            "    last_message_preview = ?, "
            "    last_message_sender_id = ? "
            "WHERE id = ?",
            (preview, sender_id, conv_id),
        )
        # Sender has now "read" their own message.
        conn.execute(
            "UPDATE participants SET last_read_message_id = ? "
            "WHERE conversation_id = ? AND user_id = ?",
            (msg_id, conv_id, sender_id),
        )
        row = conn.execute(
            f"SELECT {_MSG_COLS} FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        result = _hydrate_message(conn, row)
        conn.commit()
        return result
    finally:
        conn.close()


def edit_message(msg_id: int, sender_id: int, new_body: str) -> dict | None:
    """Edit a message if and only if the caller is its sender and the
    edit happens within MESSAGE_MUTABLE_SECONDS of creation. Returns the
    updated row, or None if the edit was rejected."""
    new_body = new_body.strip()
    if not new_body:
        return None
    conn = _conn()
    try:
        r = conn.execute(
            "SELECT id, sender_id, created_at, deleted_at FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        if not r or r["sender_id"] != sender_id or r["deleted_at"]:
            return None
        dt = conn.execute(
            "SELECT CAST(strftime('%s','now') AS INTEGER) - "
            "CAST(strftime('%s', created_at) AS INTEGER) AS dt FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        if dt is None or dt["dt"] is None or dt["dt"] > MESSAGE_MUTABLE_SECONDS:
            return None
        conn.execute(
            "UPDATE messages SET body = ?, edited_at = datetime('now') WHERE id = ?",
            (new_body, msg_id),
        )
        # Refresh the conversation's preview if this was the latest one.
        conn.execute(
            "UPDATE conversations SET last_message_preview = ? "
            "WHERE id = (SELECT conversation_id FROM messages WHERE id = ?) "
            "  AND last_message_sender_id = ?",
            (new_body[:140], msg_id, sender_id),
        )
        row = conn.execute(
            f"SELECT {_MSG_COLS} FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        out = _hydrate_message(conn, row)
        conn.commit()
        return out
    finally:
        conn.close()


def delete_message(msg_id: int, sender_id: int) -> dict | None:
    """Soft delete (sets deleted_at) within the mutable window."""
    conn = _conn()
    try:
        r = conn.execute(
            "SELECT id, sender_id, conversation_id, deleted_at FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        if not r or r["sender_id"] != sender_id or r["deleted_at"]:
            return None
        dt = conn.execute(
            "SELECT CAST(strftime('%s','now') AS INTEGER) - "
            "CAST(strftime('%s', created_at) AS INTEGER) AS dt FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        if dt is None or dt["dt"] is None or dt["dt"] > MESSAGE_MUTABLE_SECONDS:
            return None
        conn.execute(
            "UPDATE messages SET deleted_at = datetime('now') WHERE id = ?",
            (msg_id,),
        )
        # If this was the last preview in the conversation, repoint to
        # the most recent surviving message (or clear it).
        latest = conn.execute(
            "SELECT id, body, sender_id FROM messages "
            "WHERE conversation_id = ? AND deleted_at IS NULL "
            "ORDER BY id DESC LIMIT 1",
            (r["conversation_id"],),
        ).fetchone()
        if latest:
            conn.execute(
                "UPDATE conversations SET last_message_preview = ?, last_message_sender_id = ? "
                "WHERE id = ?",
                (latest["body"][:140], latest["sender_id"], r["conversation_id"]),
            )
        else:
            conn.execute(
                "UPDATE conversations SET last_message_preview = NULL, last_message_sender_id = NULL "
                "WHERE id = ?",
                (r["conversation_id"],),
            )
        row = conn.execute(
            f"SELECT {_MSG_COLS} FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
        out = _hydrate_message(conn, row)
        conn.commit()
        return out
    finally:
        conn.close()


def participant_ids(conv_id: int) -> list[int]:
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT user_id FROM participants WHERE conversation_id = ?",
            (conv_id,),
        ).fetchall()
        return [r["user_id"] for r in rows]
    finally:
        conn.close()


def mark_read(conv_id: int, user_id: int, message_id: int) -> None:
    conn = _conn()
    try:
        conn.execute("""
            UPDATE participants
            SET last_read_message_id = MAX(COALESCE(last_read_message_id, 0), ?)
            WHERE conversation_id = ? AND user_id = ?
        """, (message_id, conv_id, user_id))
        conn.commit()
    finally:
        conn.close()


def insert_notification(user_id: int, kind: str, title: str, body: str,
                        data: dict | None = None) -> dict:
    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO notifications (user_id, kind, title, body, data_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, kind, title, body, json.dumps(data) if data else None),
        )
        nid = cur.lastrowid
        conn.commit()
        return {
            "id": nid,
            "user_id": user_id,
            "kind": kind,
            "title": title,
            "body": body,
            "data": data,
            "read_at": None,
        }
    finally:
        conn.close()


def list_notifications(user_id: int, unread_only: bool = False, limit: int = 50) -> list[dict]:
    conn = _conn()
    try:
        if unread_only:
            rows = conn.execute("""
                SELECT id, kind, title, body, data_json, read_at, created_at
                FROM notifications
                WHERE user_id = ? AND read_at IS NULL
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, kind, title, body, data_json, read_at, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        out = []
        for r in rows:
            data = None
            if r["data_json"]:
                try:
                    data = json.loads(r["data_json"])
                except json.JSONDecodeError:
                    data = None
            out.append({
                "id": r["id"],
                "kind": r["kind"],
                "title": r["title"],
                "body": r["body"],
                "data": data,
                "read_at": r["read_at"],
                "created_at": r["created_at"],
            })
        return out
    finally:
        conn.close()


def mark_notifications_read(user_id: int, ids: list[int] | None = None) -> int:
    conn = _conn()
    try:
        if ids:
            placeholders = ",".join("?" * len(ids))
            cur = conn.execute(
                f"UPDATE notifications SET read_at = datetime('now') "
                f"WHERE user_id = ? AND read_at IS NULL AND id IN ({placeholders})",
                (user_id, *ids),
            )
        else:
            cur = conn.execute(
                "UPDATE notifications SET read_at = datetime('now') "
                "WHERE user_id = ? AND read_at IS NULL",
                (user_id,),
            )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def get_anna_user_id() -> int | None:
    """Return the user_id of the Anna agent, or None if not seeded."""
    conn = _conn()
    try:
        conn.execute(f"ATTACH DATABASE '{EMPLOYEES_DB_PATH}' AS emp")
        r = conn.execute(
            "SELECT id FROM emp.users WHERE user_role = 'agent' "
            "AND first_name = 'Anna' LIMIT 1"
        ).fetchone()
        return r["id"] if r else None
    finally:
        conn.close()


def ensure_anna_conversation(user_id: int) -> dict | None:
    """Find or create the Anna DM for `user_id`. Anna conversations are
    treated like DMs but use channel='anna' so the chat_routes layer can
    detect them and route messages through the Claude responder."""
    anna_id = get_anna_user_id()
    if anna_id is None or anna_id == user_id:
        return None
    a, b = sorted((user_id, anna_id))
    conn = _conn()
    try:
        row = conn.execute("""
            SELECT c.id FROM conversations c
            WHERE c.channel = 'anna' AND c.kind = 'dm'
              AND EXISTS (SELECT 1 FROM participants p WHERE p.conversation_id = c.id AND p.user_id = ?)
              AND EXISTS (SELECT 1 FROM participants p WHERE p.conversation_id = c.id AND p.user_id = ?)
              AND (SELECT COUNT(*) FROM participants p WHERE p.conversation_id = c.id) = 2
            LIMIT 1
        """, (a, b)).fetchone()
        if row:
            cid = row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO conversations (channel, kind, title, created_by) "
                "VALUES ('anna', 'dm', 'Anna', ?)",
                (user_id,),
            )
            cid = cur.lastrowid
            conn.executemany(
                "INSERT INTO participants (conversation_id, user_id) VALUES (?, ?)",
                [(cid, user_id), (cid, anna_id)],
            )
            conn.commit()
        return get_conversation(cid, user_id)
    finally:
        conn.close()


def conversation_channel(conv_id: int) -> str | None:
    conn = _conn()
    try:
        r = conn.execute(
            "SELECT channel FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        return r["channel"] if r else None
    finally:
        conn.close()


# Initialize schema at import time so callers don't have to remember.
init_schema()
