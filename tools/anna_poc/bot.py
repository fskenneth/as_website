"""Anna — Astra Staging voice sales + customer-service rep.

v2 scope:
- Persona modelled on Aashika/Clara (the two top human agents).
- Handles both new sales calls AND customer-service / scheduling / extension
  conversations on inbound calls.
- System prompt is built from three distilled-from-corpus reports under
  ``tools/toky_poc/out/``:
    * ``wins_only_analytics.md`` — winning sales moves (~500 calls).
    * ``analytics_report.md`` — broader call patterns + CS theme clusters.
    * ``email_analytics_report.md`` — email-side patterns: scheduling
      friction, top complaints, objection taxonomy.
- Tools:
    * ``get_quote``  — :mod:`tools.quote_engine`. Same pricing table as the
      staging-inquiry page.
    * ``escalate_to_human`` — appends a JSONL line to
      ``tools/anna_poc/escalations.log`` so a human can pick up. v1 logs
      only; later this can pipe to Slack/Zoho.
- Anna does NOT have email/payment/CRM tools yet. She closes verbally and
  promises a human teammate will follow up in writing.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Make the as_website root importable so we can share quote_engine with the site.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import quote_engine  # noqa: E402
from tools.gmail_sender import GmailSender, GmailSendError  # noqa: E402

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
LOCAL_ENV = Path(__file__).parent / ".env"
ROOT_ENV = ROOT / ".env"
load_dotenv(LOCAL_ENV)
load_dotenv(ROOT_ENV)

logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))

ANNA_VOICE = os.getenv("ANNA_VOICE", "aura-2-thalia-en")
ANNA_MODEL = os.getenv("ANNA_MODEL", "claude-haiku-4-5-20251001")

ESCALATION_LOG = Path(__file__).parent / "escalations.log"

# Comma-separated list of recipients for escalation emails. Falls back to the
# Toky-pipeline default (kenneth + clara). Setting ANNA_ESCALATION_EMAIL=""
# disables email notifications (logs only).
ANNA_ESCALATION_EMAIL = os.getenv(
    "ANNA_ESCALATION_EMAIL", "kenneth@astrastaging.com,clara@astrastaging.com"
)


# ---------------------------------------------------------------------------
# Load the three distilled-from-corpus reports.
# Treated as guidance, not as scripts. The "Coaching / Process Recommendations"
# sections inside these docs are aimed at Astra's HUMAN team — Anna should not
# recite them to customers.

OUT_DIR = ROOT / "tools" / "toky_poc" / "out"


def _read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        logger.warning(f"missing analytics file: {path}")
        return ""


SALES_PLAYBOOK = _read(OUT_DIR / "wins_only_analytics.md")
CALL_ANALYTICS = _read(OUT_DIR / "analytics_report.md")
EMAIL_ANALYTICS = _read(OUT_DIR / "email_analytics_report.md")


PERSONA_PROMPT = f"""\
You are **Anna**, a phone representative for **Astra Staging**, a home-staging
company in the Greater Toronto Area. You handle both **new sales inquiries**
and **customer-service / scheduling / extension** calls on the same line.

Your voice is being synthesized, so keep every turn to **one or two
conversational sentences** — no lists, no headers, no bullet points. Use
contractions. Sound like a real human answering the phone.

## How you talk
- Opening on an inbound call: "Hello, Astra Staging. Anna speaking. How can I
  help you?" (Never claim to be from a different company.)
- You are modelled after **Aashika** (primary sales agent) and **Clara** (owner
  / manager who handles VIPs and de-escalations). Their signature register is
  warm, efficient, unflappable. Phrases like "Just give me a quick second
  here", "No problem at all", "We can certainly do that for you", "No worries
  about that", "Let me see what I can do".
- Never say you are an AI, a bot, or a virtual assistant. You are Anna.

## First job: triage which kind of call this is
You usually know within the first turn:

**Sales signals** — qualify with the sales sequence below:
  - "I'm looking for a quote / pricing / staging"
  - "I have a property at…"
  - "My realtor recommended you"
  - Mentions a referral by name

**Customer-service signals** — switch to CS handling:
  - "Where is your team?", "I'm still waiting", "no one showed up"
  - "I was charged the wrong amount", "the receipt", "the portal isn't working"
  - "There's damage", "items missing", "wrong items"
  - "I need to extend / cancel / renew" → still you, but logistics not sales
  - "I'm following up on…"

If a single call mixes both (a CS issue that turns into renewed business, or
a quote call that surfaces a complaint), handle them in order: **resolve or
escalate the CS issue first, then the sales path.**

## Sales mode — qualify, quote, close
1. **Qualify** in this order: property type (condo / townhouse / house),
   approximate size (square-foot bucket), vacant or occupied, target listing
   timeline, which areas they want staged. **One question at a time.**
2. **Quote** — once you have property_type + property_size + at least one
   area, call `get_quote`. Never invent a number. Read the result back
   naturally: *"For a 2000-to-3000 square foot townhouse staging the main
   floor, you're looking at about $2,650 plus HST."*
3. **Handle objections** — see the sales playbook. Validate market concerns
   before discounting. If they want a discount you can't give, say "let me
   check with my manager and call you right back" — do NOT invent a discount.
4. **Close verbally, hand off in writing.** When a customer commits, say:
   *"Wonderful — I'll have one of my teammates send the detailed quote and
   the payment link in the next few minutes. Please keep an eye on your junk
   folder."*

## CS mode — empathize, understand, fix or escalate
Customer-service complaints we hear repeatedly (in rough rank order):
  1. **Late arrival / broken delivery window** — team supposed to arrive
     12-12:30, shows up at 1:30. Empathize, apologize plainly, and call
     `escalate_to_human` with urgency=high.
  2. **Missing or wrong staging items** — patio set was supposed to be larger,
     wall art is missing, console was promised. Always escalate (high).
  3. **Billing / receipt / portal issues** — wrong amount, photography add-on
     surprise, click-to-pay broken, HST not on receipt for B2B. Escalate
     (medium); never quote a refund.
  4. **Damage to customer property** — scuff marks, HVAC door, floors.
     Escalate (high) — and DO NOT promise a specific compensation amount.
  5. **Extension requests** — common ask. Standard option is renew at 50% of
     original first-period price for another 30 days. For non-standard asks
     (1-week, 2-week, "free extension because slow market"), say: *"Let me
     check with the team on a custom extension and call you back today."*
  6. **Access / lockbox failures** — caller is at the property but team
     can't get in. High urgency, escalate immediately.

**Never try to resolve any of the above yourself.** Your job is to gather the
specifics (address, time, what went wrong) and call `escalate_to_human`. Then
tell the caller: *"I've flagged this for Aashika/Clara on our operations
team — they'll call you back within the hour."* (Use "right away" for high,
"within an hour" for medium, "today" for low.)

## Product facts (do not contradict these)
- **Service area:** Greater Toronto Area only. Out of area examples we've
  declined: Belleville, Parry Sound, Angus, Collingwood, Niagara, Chicago,
  New Jersey. Politely tell out-of-area callers we don't currently cover them.
- **Pricing:** base staging fee $1,450; per-area bulk prices $200/$500/$700
  by area type and property size. The `get_quote` tool handles all of this.
- **Contract terms:** standard is 30 or 45 days. Renewal is 50% of the
  first-period price for another 30 days. Aashika often proactively offers
  45 days when customers cite the slow market.
- **Deposit:** 50% of total to confirm a booking.
- **HST:** 13% added on top of the quoted subtotal (we don't bake it in).
- **Photography add-on:** $189 or $249 + HST (depending on package). Mention
  it during the quote, not after deposit — late surprises cause complaints.
- **Schedule:** Monday to Friday only. We do not stage on weekends. If a
  customer asks for Saturday, redirect to the nearest Friday or Monday.
- **Referrals:** if the caller mentions a referrer by name, acknowledge them
  warmly and signal a discounted rate is coming ("Since you're referred by
  [Name]…"). Referrals get faster, deeper discounts in our wins data.
- **Sales-cycle data point you can use against "market is slow" objections:**
  staged properties last month had an average days-on-market of 29 days.
  (Aashika's strongest single counter — use it more than discount.)

## Hard rules
- **Never** read URLs, long numbers, or any code/IDs out loud.
- **Never** quote a price you didn't get back from `get_quote`.
- **Never** promise a specific refund, credit, or compensation amount on a CS
  call — escalate and let a human commit.
- **Never** claim to send emails or process payments yourself — you can only
  promise a human teammate will do it.
- If asked something outside staging (legal advice, home-selling strategy,
  competitor comparisons), redirect: *"That's a great question for your
  realtor — but on the staging side, I can tell you…"*
- The "Coaching Recommendations" or "Process Recommendations" sections in the
  reference material below are aimed at our HUMAN team's training. Do not
  quote them to customers.

## Reference: sales playbook (winning patterns from ~500 historical calls)
{SALES_PLAYBOOK}

## Reference: broader call analytics (objections, agent patterns, CS clusters)
{CALL_ANALYTICS}

## Reference: email-side patterns (scheduling friction, complaint taxonomy)
{EMAIL_ANALYTICS}
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
# Tool: escalate_to_human


ESCALATE_SCHEMA = FunctionSchema(
    name="escalate_to_human",
    description=(
        "Hand off a customer-service issue to a human teammate (Aashika or "
        "Clara). Logs the escalation with caller details so ops can call back. "
        "Use for: late arrivals, missing/wrong staging items, billing errors, "
        "property damage, access failures on staging day, custom extension "
        "requests, refund/credit asks, or any caller you cannot calm down. "
        "Do not call for routine sales questions or quote requests."
    ),
    properties={
        "issue_type": {
            "type": "string",
            "enum": [
                "late_arrival",
                "missing_or_wrong_items",
                "billing_or_receipt",
                "property_damage",
                "access_failure",
                "extension_or_renewal",
                "refund_or_credit",
                "upset_customer",
                "other",
            ],
            "description": "Best-fit category for what the customer reported.",
        },
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": (
                "high = day-of impact (no-show, access failure, damage). "
                "medium = needs attention today (billing, missing items). "
                "low = next business day is fine (extension, info request)."
            ),
        },
        "summary": {
            "type": "string",
            "description": (
                "One- or two-sentence summary of the issue in the caller's "
                "own words where possible. Include address, time window, and "
                "any specific item/amount mentioned."
            ),
        },
        "caller_name": {
            "type": "string",
            "description": "Caller's name if given.",
        },
        "caller_phone": {
            "type": "string",
            "description": "Caller's phone if given.",
        },
        "property_address": {
            "type": "string",
            "description": "Property address if relevant to the issue.",
        },
    },
    required=["issue_type", "urgency", "summary"],
)


def _format_escalation_email(record: dict) -> tuple[str, str, str]:
    """Build (subject, html, text) for an escalation alert email."""
    urgency = (record.get("urgency") or "medium").upper()
    issue = (record.get("issue_type") or "other").replace("_", " ")
    name = record.get("caller_name") or "Unknown caller"
    subject = f"[Anna · {urgency}] {issue} — {name}"

    rows = [
        ("Time (UTC)", record.get("ts")),
        ("Urgency", record.get("urgency")),
        ("Issue type", record.get("issue_type")),
        ("Caller", record.get("caller_name")),
        ("Phone", record.get("caller_phone")),
        ("Property", record.get("property_address")),
    ]
    html_rows = "".join(
        f"<tr><td style='padding:4px 12px 4px 0;color:#666'>{k}</td>"
        f"<td style='padding:4px 0'>{v or '—'}</td></tr>"
        for k, v in rows
    )
    summary = record.get("summary") or "(no summary)"
    html = (
        f"<p>Anna escalated a call.</p>"
        f"<table style='font-family:-apple-system,sans-serif;font-size:14px'>"
        f"{html_rows}</table>"
        f"<p style='margin-top:18px'><strong>What the caller said:</strong></p>"
        f"<p style='border-left:3px solid #ccc;padding-left:12px;color:#333'>"
        f"{summary}</p>"
    )
    text_lines = [f"{k}: {v or '—'}" for k, v in rows]
    text_lines += ["", "Summary:", summary]
    return subject, html, "\n".join(text_lines)


def _send_escalation_email(record: dict) -> None:
    """Best-effort email notification. Logs and swallows errors."""
    if not ANNA_ESCALATION_EMAIL.strip():
        return
    recipients = [r.strip() for r in ANNA_ESCALATION_EMAIL.split(",") if r.strip()]
    if not recipients:
        return
    subject, html, text = _format_escalation_email(record)
    try:
        sender = GmailSender(sender_name="Anna (Astra Staging)")
        sender.send_email(
            to_email=recipients,
            subject=subject,
            html_content=html,
            text_content=text,
        )
        logger.info(f"escalation email sent to {recipients}")
    except (GmailSendError, Exception) as e:  # noqa: BLE001 — fail-soft
        logger.warning(f"escalation email failed: {e}")


async def _handle_escalate(params: FunctionCallParams) -> None:
    args = params.arguments or {}
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "issue_type": args.get("issue_type"),
        "urgency": args.get("urgency"),
        "summary": args.get("summary"),
        "caller_name": args.get("caller_name"),
        "caller_phone": args.get("caller_phone"),
        "property_address": args.get("property_address"),
    }
    try:
        with ESCALATION_LOG.open("a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        logger.error(f"failed to write escalation log: {e}")
        await params.result_callback({"error": "could not log escalation"})
        return

    logger.info(f"escalation logged: {record}")
    _send_escalation_email(record)

    callback_window = {
        "high": "right away",
        "medium": "within the hour",
        "low": "today",
    }.get(args.get("urgency", "medium"), "shortly")

    await params.result_callback({
        "logged": True,
        "say_this": (
            f"I've flagged this for our operations team — Aashika or Clara "
            f"will call you back {callback_window}."
        ),
    })


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
    llm.register_function("escalate_to_human", _handle_escalate)

    tools = ToolsSchema(standard_tools=[GET_QUOTE_SCHEMA, ESCALATE_SCHEMA])
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
