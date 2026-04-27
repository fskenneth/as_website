"""
/api/v1/chat/* — internal team chat endpoints (Bearer token auth).

Phase 1 ships only the 'internal' channel; the schema is already
multi-channel so future WhatsApp/SMS/Anna/email adapters slot in
without migration.
"""
import asyncio
import json
import mimetypes
import os
import uuid
from datetime import datetime

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, StreamingResponse

from . import anna_service, chat_db, employees_db
from .chat_bus import bus


def _bearer_token(request: Request):
    auth = request.headers.get("authorization", "") or request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    return auth[7:].strip() or None


def _api_user(request: Request):
    """Bearer-token auth for mobile clients; falls back to portal session
    cookie so the web UI (which logs in via /api/auth/signin) reuses the
    same routes without juggling two token formats."""
    token = _bearer_token(request)
    if token:
        u = employees_db.get_user_by_session(token)
        if u:
            return u
    cookie_token = request.cookies.get("astra_session_employee")
    if cookie_token:
        return employees_db.get_user_by_session(cookie_token)
    return None


def register(rt):
    """Attach /api/v1/chat/* handlers to the FastHTML router."""

    @rt("/api/v1/chat/employees")
    def chat_employees(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        return JSONResponse({
            "employees": chat_db.list_employees(exclude_user_id=user["id"]),
        })

    @rt("/api/v1/chat/conversations", methods=["POST"])
    async def chat_create_conversation(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        kind = (data.get("kind") or "dm").lower()
        try:
            if kind == "dm":
                other_id = int(data.get("user_id") or 0)
                if not other_id:
                    return JSONResponse({"error": "user_id required"}, status_code=400)
                conv = chat_db.find_or_create_dm(user["id"], other_id)
            elif kind == "group":
                title = (data.get("title") or "").strip()
                ids = data.get("user_ids") or []
                ids = [int(x) for x in ids if x]
                conv = chat_db.create_group(user["id"], title, ids)
            else:
                return JSONResponse({"error": "kind must be 'dm' or 'group'"}, status_code=400)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

        # Notify other participants that a new conversation appeared.
        members = [m["id"] for m in conv["members"] if m["id"] != user["id"]]
        if members:
            bus.publish(members, "conversation_created", {"conversation_id": conv["id"]})
        return JSONResponse({"conversation": conv})

    @rt("/api/v1/chat/conversations")
    def chat_list_conversations(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        archived = request.query_params.get("archived") in ("1", "true", "yes")
        if not archived:
            # Lazy-create the user's Anna DM on first list — guarantees Anna
            # is always present at the top without a setup step.
            chat_db.ensure_anna_conversation(user["id"])
        convs = chat_db.list_conversations(user["id"], archived=archived)
        if not archived:
            # Anna stays pinned at the top regardless of pin order.
            anna_idx = next(
                (i for i, c in enumerate(convs) if c.get("channel") == "anna"), None,
            )
            if anna_idx is not None and anna_idx != 0:
                convs.insert(0, convs.pop(anna_idx))
        return JSONResponse({"conversations": convs})

    @rt("/api/v1/chat/conversations/reorder", methods=["POST"])
    async def chat_reorder(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        ids = data.get("ids") or []
        if not isinstance(ids, list):
            return JSONResponse({"error": "ids must be a list"}, status_code=400)
        try:
            ids = [int(x) for x in ids]
        except (TypeError, ValueError):
            return JSONResponse({"error": "ids must be integers"}, status_code=400)
        # Filter out conversations that don't belong to this user.
        ids = [cid for cid in ids if chat_db.is_participant(cid, user["id"])]
        n = chat_db.set_pinned_order(user["id"], ids)
        return JSONResponse({"ok": True, "updated": n})

    @rt("/api/v1/chat/conversations/{conv_id}/archive", methods=["POST"])
    async def chat_archive(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        try:
            data = await request.json()
        except Exception:
            data = {}
        archived = bool(data.get("archived", True))
        ok = chat_db.set_archived(conv_id, user["id"], archived)
        return JSONResponse({"ok": ok, "archived": archived})

    @rt("/api/v1/chat/conversations/{conv_id}", methods=["DELETE"])
    async def chat_delete(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if (user.get("user_role") or "").lower() != "owner":
            return JSONResponse({"error": "Only owners can delete chats"}, status_code=403)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        # Don't let anyone delete Anna's conversation — she's always available.
        if chat_db.conversation_channel(conv_id) == "anna":
            return JSONResponse({"error": "Cannot delete Anna"}, status_code=400)
        recipients = chat_db.participant_ids(conv_id)
        ok = chat_db.delete_conversation(conv_id)
        if ok:
            bus.publish(recipients, "conversation_deleted", {"conversation_id": conv_id})
        return JSONResponse({"ok": ok})

    @rt("/api/v1/chat/conversations/{conv_id}")
    def chat_get_conversation(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        conv = chat_db.get_conversation(conv_id, user["id"])
        if not conv:
            return JSONResponse({"error": "Not found"}, status_code=404)
        return JSONResponse({"conversation": conv})

    @rt("/api/v1/chat/conversations/{conv_id}/messages", methods=["POST"])
    async def chat_send_message(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        body = (data.get("body") or "").strip()
        if not body:
            return JSONResponse({"error": "body required"}, status_code=400)
        reply_to = data.get("reply_to_message_id")
        if reply_to is not None:
            try:
                reply_to = int(reply_to)
            except (TypeError, ValueError):
                reply_to = None
        try:
            msg = chat_db.insert_message(
                conv_id, user["id"], body,
                reply_to_message_id=reply_to,
            )
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

        recipients = chat_db.participant_ids(conv_id)
        # Push the message to every participant's SSE channel (including the
        # sender — their other tabs/devices need it too).
        bus.publish(recipients, "message", msg)

        # Persist a notification + push it for everyone except the sender.
        # Skip notifications for Anna's "human-side" — she sees nothing.
        anna_id = chat_db.get_anna_user_id()
        others = [uid for uid in recipients if uid != user["id"] and uid != anna_id]
        for uid in others:
            note = chat_db.insert_notification(
                user_id=uid,
                kind="chat_message",
                title=msg["sender"]["display_name"],
                body=msg["body"][:140],
                data={"conversation_id": conv_id, "message_id": msg["id"]},
            )
            bus.publish([uid], "notification", note)

        # If this is an Anna conversation, kick off her reply asynchronously.
        if chat_db.conversation_channel(conv_id) == "anna":
            asyncio.create_task(anna_service.respond(conv_id, user["id"], user))

        return JSONResponse({"message": msg})

    @rt("/api/v1/chat/messages/{msg_id}", methods=["PATCH"])
    async def chat_edit_message(request: Request, msg_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        body = (data.get("body") or "").strip()
        if not body:
            return JSONResponse({"error": "body required"}, status_code=400)
        updated = chat_db.edit_message(msg_id, user["id"], body)
        if not updated:
            return JSONResponse(
                {"error": "Cannot edit (not yours, deleted, or older than 10s)"},
                status_code=403,
            )
        bus.publish(
            chat_db.participant_ids(updated["conversation_id"]),
            "message_updated", updated,
        )
        return JSONResponse({"message": updated})

    @rt("/api/v1/chat/conversations/{conv_id}/messages/upload", methods=["POST"])
    async def chat_send_with_attachment(request: Request, conv_id: int):
        """Multipart endpoint that creates a message with one attached file.
        Form fields: `file` (binary, required), `body` (text, optional),
        `reply_to_message_id` (int as string, optional).
        Returns the hydrated message including the attachment URL."""
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        try:
            form = await request.form()
        except Exception:
            return JSONResponse({"error": "Invalid form"}, status_code=400)
        upload = form.get("file")
        if upload is None or not hasattr(upload, "filename"):
            return JSONResponse({"error": "file required"}, status_code=400)
        body = (form.get("body") or "").strip()
        reply_to_raw = form.get("reply_to_message_id")
        reply_to: int | None = None
        if reply_to_raw:
            try:
                reply_to = int(reply_to_raw)
            except ValueError:
                reply_to = None

        # Persist a message row first (body may be empty if it's a pure
        # attachment send; allow that).
        try:
            msg = chat_db.insert_message(
                conv_id, user["id"], body or "📎",
                reply_to_message_id=reply_to,
            )
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

        # Save the file under data/chat_media/<conv_id>/<msg_id>_<uuid>.<ext>
        chat_db.CHAT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        conv_dir = chat_db.CHAT_MEDIA_DIR / str(conv_id)
        conv_dir.mkdir(parents=True, exist_ok=True)
        original = upload.filename or "upload"
        _, ext = os.path.splitext(original)
        ext = (ext or "").lower()[:8]
        unique = f"{msg['id']}_{uuid.uuid4().hex[:8]}{ext}"
        target = conv_dir / unique
        data = await upload.read()
        with open(target, "wb") as f:
            f.write(data)

        mime = upload.content_type or mimetypes.guess_type(original)[0] or "application/octet-stream"
        kind = (
            "photo" if mime.startswith("image/") else
            "video" if mime.startswith("video/") else
            "file"
        )
        chat_db.insert_attachment(
            message_id=msg["id"],
            kind=kind,
            file_path=str(target),
            mime_type=mime,
            size=len(data),
            original_name=original,
        )
        # Refresh hydrated message to include the attachment URL.
        full = chat_db.get_message(msg["id"]) or msg

        recipients = chat_db.participant_ids(conv_id)
        bus.publish(recipients, "message", full)
        anna_id = chat_db.get_anna_user_id()
        for uid in recipients:
            if uid == user["id"] or uid == anna_id:
                continue
            note = chat_db.insert_notification(
                user_id=uid, kind="chat_message",
                title=full["sender"]["display_name"],
                body=(body or f"📎 {original}")[:140],
                data={"conversation_id": conv_id, "message_id": full["id"]},
            )
            bus.publish([uid], "notification", note)
        return JSONResponse({"message": full})

    @rt("/api/v1/chat/attachments/{att_id}")
    def chat_get_attachment(request: Request, att_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        att = chat_db.get_attachment(att_id)
        if not att:
            return JSONResponse({"error": "Not found"}, status_code=404)
        if not chat_db.is_participant(att["conversation_id"], user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        path = att["file_path"]
        if not os.path.isfile(path):
            return JSONResponse({"error": "File missing"}, status_code=410)
        return FileResponse(
            path,
            media_type=att["mime_type"] or "application/octet-stream",
            filename=att["original_name"] or os.path.basename(path),
        )

    @rt("/api/v1/chat/messages/{msg_id}/reactions", methods=["POST"])
    async def chat_react(request: Request, msg_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        emoji = (data.get("emoji") or "").strip()
        if not emoji:
            return JSONResponse({"error": "emoji required"}, status_code=400)
        updated = chat_db.toggle_reaction(msg_id, user["id"], emoji)
        if not updated:
            return JSONResponse({"error": "Cannot react"}, status_code=403)
        bus.publish(
            chat_db.participant_ids(updated["conversation_id"]),
            "message_updated", updated,
        )
        return JSONResponse({"message": updated})

    @rt("/api/v1/chat/messages/{msg_id}", methods=["DELETE"])
    async def chat_delete_message(request: Request, msg_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        deleted = chat_db.delete_message(msg_id, user["id"])
        if not deleted:
            return JSONResponse(
                {"error": "Cannot delete (not yours or older than 10s)"},
                status_code=403,
            )
        bus.publish(
            chat_db.participant_ids(deleted["conversation_id"]),
            "message_updated", deleted,
        )
        return JSONResponse({"message": deleted})

    @rt("/api/v1/chat/conversations/{conv_id}/messages")
    def chat_list_messages(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        try:
            limit = min(int(request.query_params.get("limit", "50")), 200)
        except ValueError:
            limit = 50
        before_raw = request.query_params.get("before")
        before_id = int(before_raw) if before_raw and before_raw.isdigit() else None
        msgs = chat_db.list_messages(conv_id, limit=limit, before_id=before_id)
        return JSONResponse({"messages": msgs})

    @rt("/api/v1/chat/conversations/{conv_id}/read", methods=["POST"])
    async def chat_mark_read(request: Request, conv_id: int):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        if not chat_db.is_participant(conv_id, user["id"]):
            return JSONResponse({"error": "Not a participant"}, status_code=403)
        try:
            data = await request.json()
        except Exception:
            data = {}
        message_id = int(data.get("message_id") or 0)
        if not message_id:
            msgs = chat_db.list_messages(conv_id, limit=1)
            message_id = msgs[-1]["id"] if msgs else 0
        if message_id:
            chat_db.mark_read(conv_id, user["id"], message_id)
            bus.publish([user["id"]], "read_receipt",
                        {"conversation_id": conv_id, "message_id": message_id})
        return JSONResponse({"ok": True, "message_id": message_id})

    @rt("/api/v1/chat/notifications")
    def chat_list_notifications(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        unread_only = request.query_params.get("unread") in ("1", "true", "yes")
        return JSONResponse({
            "notifications": chat_db.list_notifications(user["id"], unread_only=unread_only),
        })

    @rt("/api/v1/chat/notifications/read", methods=["POST"])
    async def chat_mark_notifications_read(request: Request):
        user = _api_user(request)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        try:
            data = await request.json()
        except Exception:
            data = {}
        ids = data.get("ids")
        if isinstance(ids, list):
            ids = [int(x) for x in ids if str(x).isdigit()]
        else:
            ids = None
        n = chat_db.mark_notifications_read(user["id"], ids=ids)
        return JSONResponse({"ok": True, "updated": n})

    @rt("/api/v1/chat/sse")
    async def chat_sse(request: Request):
        # SSE clients can't send custom headers cross-domain, so we accept the
        # bearer token via ?token= query string in addition to the header.
        token = _bearer_token(request) or request.query_params.get("token")
        user = None
        if token:
            user = employees_db.get_user_by_session(token)
        if not user:
            cookie_token = request.cookies.get("astra_session_employee")
            if cookie_token:
                user = employees_db.get_user_by_session(cookie_token)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        user_id = user["id"]
        queue = await bus.subscribe(user_id)

        async def event_stream():
            # Initial hello so the client knows the connection is live.
            yield ("event: hello\n"
                   f"data: {json.dumps({'user_id': user_id, 'ts': datetime.utcnow().isoformat()})}\n\n")
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        item = await asyncio.wait_for(queue.get(), timeout=20.0)
                    except asyncio.TimeoutError:
                        # Heartbeat keeps proxies / load balancers from idling
                        # the connection out at 30s.
                        yield ": ping\n\n"
                        continue
                    yield f"data: {item}\n\n"
            finally:
                await bus.unsubscribe(user_id, queue)

        headers = {
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
        return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)
