"""
OpenAI-backed transcription + summarization for the Consultation Dictate feature.

- transcribe_audio:   Whisper (whisper-1) over REST.
- summarize_consultation: gpt-4o-mini with JSON-mode structured output —
  returns key points + customer/sales-rep email drafts + suggested quote lines.

Both helpers are synchronous and short (~seconds). Route handlers can `await
asyncio.to_thread(...)` them so the event loop stays free under load.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENAI_API_BASE = "https://api.openai.com/v1"
WHISPER_MODEL = "whisper-1"
SUMMARY_MODEL = "gpt-4o-mini"

# Generous — Whisper can be slow on long files; summary is fast.
_TRANSCRIBE_TIMEOUT = httpx.Timeout(connect=10.0, read=300.0, write=120.0, pool=10.0)
_SUMMARY_TIMEOUT = httpx.Timeout(connect=10.0, read=90.0, write=30.0, pool=10.0)


class AIServiceError(RuntimeError):
    """Raised when OpenAI is unreachable, misconfigured, or returns a bad response."""


def _api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "REPLACE_WITH_ROTATED_KEY":
        raise AIServiceError(
            "OPENAI_API_KEY is not configured. Set it in as_website/.env "
            "(the Consultation Dictate feature won't work without it)."
        )
    return key


def transcribe_audio(audio_path: str, language: Optional[str] = "en") -> str:
    """Send an audio file to Whisper and return the transcript text.

    `audio_path` is a filesystem path. Whisper accepts m4a, mp3, mp4, mpeg,
    mpga, wav, webm, and others up to 25 MB — we record AAC-LC mono 16 kHz
    32 kbps on mobile so a 1-hour consultation is ~14 MB, well under.
    """
    if not os.path.exists(audio_path):
        raise AIServiceError(f"Audio file not found: {audio_path}")

    headers = {"Authorization": f"Bearer {_api_key()}"}
    data = {"model": WHISPER_MODEL, "response_format": "text"}
    if language:
        data["language"] = language

    with open(audio_path, "rb") as fh:
        files = {"file": (os.path.basename(audio_path), fh, "audio/m4a")}
        try:
            with httpx.Client(timeout=_TRANSCRIBE_TIMEOUT) as client:
                resp = client.post(
                    f"{OPENAI_API_BASE}/audio/transcriptions",
                    headers=headers,
                    data=data,
                    files=files,
                )
        except httpx.HTTPError as exc:
            raise AIServiceError(f"Whisper request failed: {exc}") from exc

    if resp.status_code != 200:
        raise AIServiceError(
            f"Whisper returned {resp.status_code}: {resp.text[:400]}"
        )

    # response_format=text → body is the raw transcript.
    return resp.text.strip()


_SUMMARY_SYSTEM_PROMPT = """You are an on-site assistant for Astra Staging, a home-staging company in Mississauga, Ontario. A staging consultant has just finished a walk-through consultation with a potential client and dictated their notes. Your job is to turn the raw dictation into structured output the consultant can act on immediately:

1. A short bulleted summary of the key points discussed.
2. A draft email FROM the consultant TO the customer confirming what was discussed and next steps. Warm but professional. Do NOT invent prices, dates, or promises not in the dictation. Sign off as "The Astra Staging Team".
3. A draft email FROM the consultant TO the sales rep (internal handoff) summarizing the visit, flagging any follow-up actions, decisions needed, and anything blocking quote preparation.
4. A list of suggested line items for a quote, if the dictation mentioned specific rooms / areas / furniture packages / add-ons. Each item has a short description. Do NOT invent prices.

Be faithful to the dictation. If information is missing (e.g., no customer name was mentioned), leave those placeholders generic ("Dear Homeowner") rather than hallucinating.

Return ONLY a JSON object matching this schema, no prose outside the JSON:
{
  "key_points": ["..."],
  "customer_email_subject": "...",
  "customer_email_body": "...",
  "sales_rep_email_subject": "...",
  "sales_rep_email_body": "...",
  "suggested_quote_lines": [{"description": "..."}]
}"""


def _build_staging_context_block(staging: Optional[dict], area_name: Optional[str]) -> str:
    """Short human-readable staging context for the LLM prompt."""
    if not staging:
        return ""
    parts = []
    name = staging.get("name") or staging.get("address")
    if name:
        parts.append(f"Property: {name}")
    cust = staging.get("customer") or {}
    full = f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip()
    if full:
        parts.append(f"Customer: {full}")
    if cust.get("email"):
        parts.append(f"Customer email: {cust['email']}")
    if staging.get("property_type"):
        parts.append(f"Property type: {staging['property_type']}")
    if staging.get("occupancy"):
        parts.append(f"Occupancy: {staging['occupancy']}")
    if area_name:
        parts.append(f"Area being discussed: {area_name}")
    return "\n".join(parts)


def summarize_consultation(
    transcript: str,
    staging: Optional[dict] = None,
    area_name: Optional[str] = None,
) -> dict:
    """Run gpt-4o-mini over the transcript and return a structured summary.

    Shape (keys always present, values may be empty):
        {
          "key_points": [str],
          "customer_email_subject": str,
          "customer_email_body": str,
          "sales_rep_email_subject": str,
          "sales_rep_email_body": str,
          "suggested_quote_lines": [{"description": str}],
        }
    """
    if not transcript or not transcript.strip():
        return _empty_summary()

    context = _build_staging_context_block(staging, area_name)
    user_content = (
        (f"Context about this consultation:\n{context}\n\n" if context else "")
        + "Consultation dictation transcript:\n\"\"\"\n"
        + transcript.strip()
        + "\n\"\"\""
    )

    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SUMMARY_MODEL,
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": _SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    }

    try:
        with httpx.Client(timeout=_SUMMARY_TIMEOUT) as client:
            resp = client.post(
                f"{OPENAI_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise AIServiceError(f"Summary request failed: {exc}") from exc

    if resp.status_code != 200:
        raise AIServiceError(
            f"Summary returned {resp.status_code}: {resp.text[:400]}"
        )

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, ValueError) as exc:
        raise AIServiceError(f"Summary response was not valid JSON: {exc}") from exc

    return _coerce_summary_shape(parsed)


def _empty_summary() -> dict:
    return {
        "key_points": [],
        "customer_email_subject": "",
        "customer_email_body": "",
        "sales_rep_email_subject": "",
        "sales_rep_email_body": "",
        "suggested_quote_lines": [],
    }


def _coerce_summary_shape(raw: dict) -> dict:
    out = _empty_summary()
    kp = raw.get("key_points")
    if isinstance(kp, list):
        out["key_points"] = [str(x) for x in kp if str(x).strip()]

    for key in (
        "customer_email_subject",
        "customer_email_body",
        "sales_rep_email_subject",
        "sales_rep_email_body",
    ):
        val = raw.get(key)
        if isinstance(val, str):
            out[key] = val.strip()

    lines = raw.get("suggested_quote_lines")
    if isinstance(lines, list):
        clean = []
        for item in lines:
            if isinstance(item, dict) and item.get("description"):
                clean.append({"description": str(item["description"]).strip()})
            elif isinstance(item, str) and item.strip():
                clean.append({"description": item.strip()})
        out["suggested_quote_lines"] = clean

    return out
