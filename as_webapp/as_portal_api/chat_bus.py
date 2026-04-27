"""
In-process SSE pub/sub for chat + notifications.

Single-process broadcaster: each connected client owns an asyncio.Queue keyed
on user_id. When a message lands or a notification fires, we look up every
recipient and `put_nowait` an event onto each of their queues. The SSE
endpoint drains the queue and writes `data: <json>\n\n` lines.

If we ever scale the webapp to multiple Uvicorn workers we'll need a
cross-process broker (Redis pub/sub or sqlite long-poll). For now one
worker handles the whole team comfortably.
"""
import asyncio
import json
from collections import defaultdict


class ChatBus:
    def __init__(self) -> None:
        self._subs: dict[int, set[asyncio.Queue]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=200)
        async with self._lock:
            self._subs[user_id].add(q)
        return q

    async def unsubscribe(self, user_id: int, q: asyncio.Queue) -> None:
        async with self._lock:
            subs = self._subs.get(user_id)
            if subs and q in subs:
                subs.discard(q)
                if not subs:
                    self._subs.pop(user_id, None)

    def publish(self, user_ids, event_type: str, payload: dict) -> None:
        """Fire-and-forget broadcast. Safe to call from sync code; queues
        are bounded so a slow consumer can't OOM the box — we drop oldest."""
        body = json.dumps({"type": event_type, "data": payload})
        for uid in set(user_ids):
            for q in list(self._subs.get(uid, ())):
                try:
                    q.put_nowait(body)
                except asyncio.QueueFull:
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    try:
                        q.put_nowait(body)
                    except asyncio.QueueFull:
                        pass

    def online_users(self) -> set[int]:
        return set(self._subs.keys())


bus = ChatBus()
