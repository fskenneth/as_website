"""Anna — Astra Staging voice sales rep (Pipecat 1.0 pipeline).

v1 sales-rep scope:
- Persona modelled on Aashika/Clara (the two top human agents).
- System prompt distilled from the wins-only analytics of ~500 historical
  Toky calls (see ``tools/toky_poc/out/wins_only_analytics.md``).
- Single tool: ``get_quote`` — calls :mod:`tools.quote_engine` (the same
  pricing table as the staging-inquiry page on as_website).
- No CRM/email tools yet. Anna closes verbally and promises a human
  teammate will follow up with the written quote + payment link.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Make the as_website root importable so we can share quote_engine with the site.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import quote_engine  # noqa: E402

from pipecat.adapters.schemas.function_schema import FunctionSchema  # noqa: E402
from pipecat.adapters.schemas.tools_schema import ToolsSchema  # noqa: E402
from pipecat.audio.vad.silero import SileroVADAnalyzer  # noqa: E402
from pipecat.pipeline.pipeline import Pipeline  # noqa: E402
from pipecat.pipeline.runner import PipelineRunner  # noqa: E402
from pipecat.pipeline.task import PipelineParams, PipelineTask  # noqa: E402
from pipecat.processors.aggregators.llm_context import LLMContext  # noqa: E402
from pipecat.processors.aggregators.llm_response_universal import (  # noqa: E402
    LLMContextAggregatorPair,
)
from pipecat.services.anthropic.llm import AnthropicLLMService  # noqa: E402
from pipecat.services.deepgram.stt import DeepgramSTTService  # noqa: E402
from pipecat.services.deepgram.tts import DeepgramTTSService  # noqa: E402
from pipecat.services.llm_service import FunctionCallParams  # noqa: E402
from pipecat.transports.base_transport import TransportParams  # noqa: E402
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection  # noqa: E402
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport  # noqa: E402

# Prefer a POC-local .env (tools/anna_poc/.env). Fall back to as_website/.env.
# dotenv won't overwrite existing values, so the local file wins on shared keys.
LOCAL_ENV = Path(__file__).parent / ".env"
ROOT_ENV = ROOT / ".env"
load_dotenv(LOCAL_ENV)
load_dotenv(ROOT_ENV)

logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))

ANNA_VOICE = os.getenv("ANNA_VOICE", "aura-2-thalia-en")
ANNA_MODEL = os.getenv("ANNA_MODEL", "claude-haiku-4-5-20251001")

# Wins-only playbook distilled from ~500 historical Toky calls. Treated as
# guidance, not a script — Anna should *sound* like Aashika/Clara, not read
# phrases verbatim.
PLAYBOOK_PATH = ROOT / "tools" / "toky_poc" / "out" / "wins_only_analytics.md"
try:
    PLAYBOOK = PLAYBOOK_PATH.read_text()
except FileNotFoundError:
    logger.warning(f"playbook not found at {PLAYBOOK_PATH}; using empty fallback")
    PLAYBOOK = ""


PERSONA_PROMPT = """\
You are **Anna**, a sales representative for **Astra Staging**, a home-staging
company in the Greater Toronto Area. Your voice is being synthesized, so keep
every turn to one or two conversational sentences — no lists, no headers, no
bullet points. Use contractions. Sound like a real human answering the phone.

## How you talk
- Opening on an inbound call: "Hello, Astra Staging. Anna speaking. How can I
  help you?" (Never claim to be from a different company.)
- You are modelled after Aashika and Clara, our two top sales reps. Their
  signature phrases are things like "Just give me a quick second here", "No
  problem at all", "We can certainly do that for you", "No worries about
  that". Use that register — warm, efficient, unflappable.
- Never say you are an AI, a bot, or a virtual assistant. You are Anna.

## The job on every call
1. **Qualify** — in this order: property type (condo / townhouse / house),
   approximate size (square-foot bucket), vacant or occupied, target listing
   timeline, which areas they want staged. Ask one question at a time.
2. **Quote** — once you have property_type + property_size + at least one
   area, call the `get_quote` tool to get the real price. Never invent a
   number. When you read the quote back, keep it short and natural: "For a
   2000 to 3000 square foot townhouse staging the main floor, you're looking
   at about $X plus HST." (HST is 13% in Ontario; don't add it yourself.)
3. **Handle objections** — see the playbook below. Validate market concerns
   before discounting. If they ask for a discount you can't unilaterally give,
   offer to "check with my manager" rather than inventing a number.
4. **Close verbally, hand off in writing** — you do NOT have email or payment
   tools yet. When a customer commits, say something like: "Wonderful — I'll
   have one of my teammates send over the detailed quote and the payment link
   in the next few minutes, please keep an eye on your junk folder."

## Product facts (do not contradict these)
- Service area: Greater Toronto Area. If a caller is outside — e.g. Belleville,
  Parry Sound, Chicago — politely tell them we don't currently cover that area.
- Base staging fee is $1450, with size uplifts built in. Per-area bulk prices
  are $200 (small), $500 (mid), $700 (large). You don't need to memorize these
  — the get_quote tool handles pricing.
- Standard contract is 30 or 45 days; renewal rate is 50% of the first-period
  price if the property doesn't sell in time.
- Deposit to confirm a booking is 50%.
- HST (13%) is added on top of the quoted subtotal.
- If the caller mentions a referral by name, acknowledge the referrer warmly
  and signal a discounted rate is coming ("Since you're referred by [Name]…").

## Conversational playbook (wins-only, use as guidance, not a script)
""" + PLAYBOOK + """

## Hard rules
- Never read URLs, long numbers, or code out loud.
- Never quote a price you didn't get back from `get_quote`.
- If asked something outside staging (legal advice, home-selling strategy,
  competitor comparisons), politely redirect: "That's a great question for
  your realtor — but on the staging side, I can tell you…"
- If a caller seems upset or reports a service issue, don't try to resolve
  it yourself. Say: "Let me have Aashika or Clara from our operations team
  call you right back about this."
"""


GREETING = "Hello, Astra Staging. Anna speaking. How can I help you?"


# ---------------------------------------------------------------------------
# Tool: get_quote


GET_QUOTE_SCHEMA = FunctionSchema(
    name="get_quote",
    description=(
        "Calculate a home-staging price quote from the Astra Staging pricing "
        "table. Call this only after you have confirmed the property type, "
        "the square-footage bucket, and at least one area to stage. Returns "
        "the subtotal (pre-HST). Uses bulk per-area pricing; item-by-item "
        "itemization is not supported in this version."
    ),
    properties={
        "property_type": {
            "type": "string",
            "enum": ["condo", "townhouse", "house"],
            "description": "Property type as confirmed by the customer.",
        },
        "property_size": {
            "type": "string",
            "enum": [
                "under-1000",
                "1000-2000",
                "2000-3000",
                "3000-4000",
                "over-4000",
            ],
            "description": (
                "Square-footage bucket. Valid combinations: condo = "
                "under-1000 / 1000-2000 / 2000-3000. townhouse = 1000-2000 "
                "/ 2000-3000 / 3000-4000. house = 2000-3000 / 3000-4000 / "
                "over-4000."
            ),
        },
        "areas": {
            "type": "array",
            "items": {"type": "string", "enum": list(quote_engine.VALID_AREAS)},
            "description": (
                "Areas the customer wants staged. Slugs match the website "
                "(e.g. 'living-room', 'master-bedroom', 'kitchen-island')."
            ),
        },
    },
    required=["property_type", "property_size", "areas"],
)


async def _handle_get_quote(params: FunctionCallParams) -> None:
    args = params.arguments or {}
    try:
        q = quote_engine.quote(
            property_type=args["property_type"],
            property_size=args["property_size"],
            areas={slug: [] for slug in args.get("areas", [])},
        )
    except (KeyError, ValueError) as e:
        logger.warning(f"get_quote failed: {e}")
        await params.result_callback({"error": str(e)})
        return

    result = {
        "subtotal": round(q.subtotal, 2),
        "base_fee": round(q.base_fee, 2),
        "currency": "CAD",
        "tax_note": "Add 13% HST on top of subtotal.",
        "areas": [
            {"area": a.area, "charged_price": round(a.charged_price, 2)}
            for a in q.areas
        ],
        "say_this": q.summary_line(),
    }
    logger.info(f"get_quote -> {result}")
    await params.result_callback(result)


# ---------------------------------------------------------------------------
# Pipeline


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
    llm.register_function("get_quote", _handle_get_quote)

    tools = ToolsSchema(standard_tools=[GET_QUOTE_SCHEMA])
    context = LLMContext(
        messages=[{"role": "system", "content": PERSONA_PROMPT}],
        tools=tools,
    )
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
        from pipecat.frames.frames import TTSSpeakFrame
        await task.queue_frames([TTSSpeakFrame(GREETING)])

    @transport.event_handler("on_client_disconnected")
    async def _on_disconnect(_transport, _client):
        logger.info("client disconnected — cancelling task")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)
