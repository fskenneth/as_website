"""FastAPI server for the Anna voice POC.

- GET /            -> serves static/index.html (mic UI)
- POST /offer      -> SDP offer/answer exchange; spawns a Pipecat pipeline
                      per new peer connection.
"""

import asyncio
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
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

webrtc_handler = SmallWebRTCRequestHandler(
    ice_servers=[],  # localhost only — no STUN needed
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
