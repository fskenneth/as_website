"""FastAPI server for the Anna voice POC.

- GET /            -> serves static/index.html (mic UI)
- POST /offer      -> SDP offer/answer exchange; spawns a Pipecat pipeline
                      per new peer connection.
"""

import asyncio
import os
from pathlib import Path

import httpx
from aiortc import RTCIceServer
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger

from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)

from bot import run_bot

HERE = Path(__file__).parent
STATIC = HERE / "static"

app = FastAPI(title="Anna Voice POC")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# STUN lets aiortc gather a server-reflexive ICE candidate so the browser can
# reach the droplet's public IP. Harmless on localhost (just an extra UDP
# round-trip that no peer ends up using).
_STUN_URLS = os.getenv(
    "ANNA_STUN_URLS",
    "stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302",
).split(",")
webrtc_handler = SmallWebRTCRequestHandler(
    ice_servers=[RTCIceServer(urls=u.strip()) for u in _STUN_URLS if u.strip()],
)


# --- Voice preview ----------------------------------------------------------
# When the dropdown changes, the page hits /preview?voice=... so the user
# hears each Aura-2 voice without starting a real WebRTC session. We cache
# the audio bytes per voice in-memory; same text every time (~9 voices total).
PREVIEW_TEXT = (
    "Hi, I'm Anna from Astra Staging. How can I help you today?"
)
PREVIEW_VOICES: set[str] = {
    "aura-2-thalia-en",
    "aura-2-luna-en",
    "aura-2-asteria-en",
    "aura-2-stella-en",
    "aura-2-athena-en",
    "aura-2-hera-en",
}
_preview_cache: dict[str, bytes] = {}
_preview_lock = asyncio.Lock()


async def _fetch_preview(voice: str) -> bytes:
    """Call Deepgram's HTTP TTS endpoint and return MP3 bytes."""
    api_key = os.environ["DEEPGRAM_API_KEY"]
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.deepgram.com/v1/speak",
            params={"model": voice, "encoding": "mp3"},
            headers={"Authorization": f"Token {api_key}"},
            json={"text": PREVIEW_TEXT},
        )
        resp.raise_for_status()
        return resp.content


@app.get("/preview")
async def preview(voice: str):
    if voice not in PREVIEW_VOICES:
        raise HTTPException(status_code=400, detail="unknown voice")
    if voice not in _preview_cache:
        async with _preview_lock:
            # Double-check inside the lock — concurrent first hits.
            if voice not in _preview_cache:
                try:
                    _preview_cache[voice] = await _fetch_preview(voice)
                except httpx.HTTPError as e:
                    logger.warning(f"preview fetch failed for {voice}: {e}")
                    raise HTTPException(status_code=502, detail="tts upstream error")
    return Response(
        content=_preview_cache[voice],
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


@app.post("/offer")
async def offer(request: Request):
    body = await request.json()
    req = SmallWebRTCRequest.from_dict(body)

    # Pull out optional client-supplied params (voice picker, etc.)
    extras = body.get("request_data") or body.get("requestData") or {}
    voice = extras.get("voice") if isinstance(extras, dict) else None

    async def _on_new_connection(connection: SmallWebRTCConnection) -> None:
        logger.info(f"new peer connection {connection.pc_id} — launching bot")
        asyncio.create_task(run_bot(connection, voice=voice))

    answer = await webrtc_handler.handle_web_request(req, _on_new_connection)
    return answer


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="info")
