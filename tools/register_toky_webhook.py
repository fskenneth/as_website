"""
Register (or list / delete) the Toky webhook that points at our m4 server.

    .venv/bin/python tools/register_toky_webhook.py list
    .venv/bin/python tools/register_toky_webhook.py register <hook_url>
    .venv/bin/python tools/register_toky_webhook.py delete <webhook_id>

The hook_url must be reachable from Toky's cloud — typically:
  - Tailscale Funnel: https://<machine>.<tailnet>.ts.net/api/v1/toky/webhook
  - Or your DigitalOcean host once migrated

Events we subscribe to (one registration per event — Toky docs show each
event handled separately):
  - inbound_call_ended
  - outbound_call_ended

Environment:
  TOKY_API_KEY — required, from .env

Gotchas to confirm with Toky support once you email them:
  1. Signing / HMAC scheme — not documented publicly.
  2. Source IP range so we can tighten the allowlist in as_webapp.
  3. Retry policy on 5xx from our webhook.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API_BASE = "https://api.toky.co/v1"
KEY = os.getenv("TOKY_API_KEY", "").strip()
if not KEY:
    print("ERROR: TOKY_API_KEY missing in .env", file=sys.stderr)
    sys.exit(2)

HEADERS = {"X-Toky-Key": KEY, "Accept": "application/json", "Content-Type": "application/json"}
EVENTS = ("inbound_call_ended", "outbound_call_ended")


def list_hooks() -> list[dict]:
    with httpx.Client(timeout=30.0) as c:
        r = c.get(f"{API_BASE}/webhooks", headers=HEADERS)
    if r.status_code != 200:
        print(f"list webhooks -> {r.status_code}: {r.text[:400]}", file=sys.stderr)
        sys.exit(1)
    body = r.json()
    items = body if isinstance(body, list) else body.get("results") or body.get("webhooks") or []
    return items


def register(hook_url: str) -> None:
    existing = list_hooks()
    existing_by_event = {w.get("event"): w for w in existing if isinstance(w, dict)}
    created = []
    for event in EVENTS:
        if event in existing_by_event and existing_by_event[event].get("hook_url") == hook_url:
            print(f"  [{event}] already registered -> id={existing_by_event[event].get('id')}")
            continue
        payload = {"event": event, "hook_url": hook_url}
        with httpx.Client(timeout=30.0) as c:
            r = c.post(f"{API_BASE}/webhooks", headers=HEADERS, json=payload)
        if r.status_code in (200, 201):
            body = r.json()
            created.append({"event": event, "id": body.get("id"), "hook_url": hook_url})
            print(f"  [{event}] registered -> id={body.get('id')}")
        else:
            print(f"  [{event}] FAILED {r.status_code}: {r.text[:300]}", file=sys.stderr)
    if created:
        print()
        print("Save these IDs if you need to delete them later:")
        print(json.dumps(created, indent=2))


def delete(webhook_id: str) -> None:
    with httpx.Client(timeout=30.0) as c:
        r = c.delete(f"{API_BASE}/webhooks/{webhook_id}", headers=HEADERS)
    print(f"delete {webhook_id} -> {r.status_code}: {r.text[:200]}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "list":
        hooks = list_hooks()
        print(f"Registered webhooks ({len(hooks)}):")
        for w in hooks:
            print(f"  id={w.get('id')}  event={w.get('event')}  url={w.get('hook_url')}")
        return 0
    if cmd == "register":
        if len(sys.argv) < 3:
            print("usage: register <hook_url>", file=sys.stderr); return 2
        register(sys.argv[2])
        return 0
    if cmd == "delete":
        if len(sys.argv) < 3:
            print("usage: delete <webhook_id>", file=sys.stderr); return 2
        delete(sys.argv[2])
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
