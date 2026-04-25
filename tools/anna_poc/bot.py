"""Anna voice POC — Pipecat 1.0 pipeline.

DG STT  ->  Claude Haiku 4.5  ->  DG Aura-2 TTS, over SmallWebRTC.
No tools, no sales logic — just chat, so we can judge voice + latency.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.services.anthropic.llm import AnthropicLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

# Prefer a POC-local .env (tools/anna_poc/.env). Fall back to as_website/.env.
# dotenv won't overwrite existing values, so the local file wins on shared keys.
LOCAL_ENV = Path(__file__).parent / ".env"
ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(LOCAL_ENV)
load_dotenv(ROOT_ENV)

logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))

ANNA_VOICE = os.getenv("ANNA_VOICE", "aura-2-thalia-en")
ANNA_MODEL = os.getenv("ANNA_MODEL", "claude-haiku-4-5-20251001")

SYSTEM_PROMPT = (
    "You are Anna, a friendly, upbeat conversationalist on a phone call. "
    "Your voice is being synthesized, so keep responses short — one or two "
    "sentences at a time, like real speech. Use contractions. Don't read "
    "lists or bullet points. If the user asks a question you can't answer, "
    "say so briefly and ask what else is on their mind. This is a casual "
    "voice test — chat about anything they bring up."
)

GREETING = "Hey, this is Anna. What's on your mind today?"


async def run_bot(
    webrtc_connection: SmallWebRTCConnection,
    voice: str | None = None,
) -> None:
    """Build and run the Pipecat pipeline for one WebRTC peer.

    Args:
        webrtc_connection: the negotiated peer.
        voice: Aura voice name (e.g. ``aura-2-luna-en``). Falls back to
            ``ANNA_VOICE`` env var, then ``aura-2-thalia-en``.
    """

    chosen_voice = voice or ANNA_VOICE
    logger.info(f"starting pipeline with voice={chosen_voice}")

    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    stt = DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"])
    tts = DeepgramTTSService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        voice=chosen_voice,
    )
    llm = AnthropicLLMService(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model=ANNA_MODEL,
    )

    context = LLMContext(messages=[{"role": "system", "content": SYSTEM_PROMPT}])
    aggregators = LLMContextAggregatorPair(context)

    pipeline = Pipeline([
        transport.input(),
        stt,
        aggregators.user(),
        llm,
        tts,
        transport.output(),
        aggregators.assistant(),
    ])

    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True))

    @transport.event_handler("on_client_connected")
    async def _on_connect(_transport, _client):
        logger.info("client connected — speaking greeting")
        # Inject a TTS frame directly so Anna says hi without waiting for the user.
        from pipecat.frames.frames import TTSSpeakFrame
        await task.queue_frames([TTSSpeakFrame(GREETING)])

    @transport.event_handler("on_client_disconnected")
    async def _on_disconnect(_transport, _client):
        logger.info("client disconnected — cancelling task")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)
