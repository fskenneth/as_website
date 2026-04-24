# Toky Call Intelligence — Technical Proposal

**Prepared for:** Astra Staging (Toronto) — sales & customer-service pipeline enhancement
**Prepared:** 2026-04-23
**Integrating with:** existing `as_webapp` FastHTML backend on the m4 Mac Mini (already using OpenAI Whisper + `gpt-4o-mini` for consultation dictation — see `as_webapp/as_portal_api/ai_service.py`)

## 1. Executive Summary

Two workstreams will be built on top of Astra Staging's existing FastHTML backend.

- **A. Historical backfill & analytics** — one-shot pull of every Toky recording since inception, batch-transcribed, then analyzed with a long-context LLM to surface sales patterns (winning language, objections, call-length vs outcome, agent performance).
- **B. Real-time per-call automation** — a Toky webhook fires on `inbound_call_ended` / `outbound_call_ended`, the audio is pulled, transcribed in minutes, and an LLM extracts structured data that creates (1) a staging-project record, (2) a draft quote using the existing pricing catalog, and (3) a customer-service task when applicable.

**Top picks:** Deepgram Nova-3 for transcription (phone-tuned, diarization, cheap, batch + stream); Claude Opus 4.7 (1M context) for historical analytics; Claude Haiku 4.5 for per-call structured extraction.

**Rough monthly spend** (30 calls/day × 5 min, see §6): ~USD $50/month steady-state. **Backfill** of 10,000 historical 5-min calls: ~USD $395 one-shot — engineering time dwarfs the API cost.

---

## 2. Toky.co API Surface (research findings)

**URLs consulted:**
- https://developer.toky.co/
- https://developer.toky.co/reference/recordings-url
- https://developer.toky.co/reference/webhooks-1
- https://developer.toky.co/reference/call-data-records-cdr
- https://developer.toky.co/reference/cdrs-by-date
- https://developer.toky.co/docs/about-data-pagination
- https://developer.toky.co/docs/how-to-register-a-webhook-with-toky
- https://developer.toky.co/docs/how-to-get-toky-call-data-records
- https://docs.bird.com/toky-en/how-to-guidestokyapp/download-call-recordings-using-the-api-reference (MessageBird/Bird-owned help since the Toky acquisition)

### 2.1 Authentication
- **Header:** `X-Toky-Key: <api_key>`
- Admin-only, single long-lived API key (generated in Toky web app → **API Key**).
- No OAuth. Treat the key as a secret; store in `.env`.

### 2.2 Listing calls (CDRs)
- Base URL: `https://api.toky.co/v1`
- `GET /cdrs` and `GET /cdrs/by-date` (date-ranged).
- **Pagination:** cursor-style, max `limit=500` per page; `next` URL until null.
- Per CDR typically: `callid`, `direction` (inbound/outbound), `agent`, phone numbers, `duration`, `state` (answered/busy/no-answer/voicemail), `date`, `record_url`. Exact schema requires the interactive "Try It" under login — **TODO verify on first real key**.

### 2.3 Downloading a recording
- `GET /recordings/{callid}` → JSON with a public-but-unguessable URL to the audio (mp3, standard Toky).
- `DELETE /recordings/{callid}` also exists.
- **No documented bulk endpoint** — workflow: page `/cdrs/by-date` → `GET /recordings/{callid}` per call → download mp3.

### 2.4 Webhooks (real-time)
- Register via `POST /webhooks` with `{event, hook_url}`; save the returned `id` (needed for `DELETE /webhooks/{id}`).
- Events relevant here:
  - `inbound_call_ended` / `outbound_call_ended` ← **primary trigger for Workstream B**
  - `new_call`, `inbound_call_answered`, `outbound_call`, `new_voicemail`, `new_sms`
- Payload includes `callid`, `direction`, agent block, `duration`, `state`, phone numbers, `date`, and **`record_url`** (saves a round-trip).

**Gaps in public docs** (ask Toky support day 1):
1. **Signature / HMAC verification** — not documented. Rely on IP allowlist until confirmed.
2. **Retry policy / delivery guarantees** — undocumented. Assume at-most-once; make handler idempotent on `callid`.
3. **Recording retention period** — not published. UCaaS norm is ~90 days. **This is the single biggest reason to start the backfill immediately.**
4. **Native transcription/AI** — nothing advertised. Roll our own (we need control anyway).

### 2.5 Ontario / Canada compliance
- One-party consent under Criminal Code s. 184 — Astra as a call party can record.
- PIPEDA still requires notification + stated purpose + opt-out alternative.
- **Action items:**
  - Add a 5-second IVR notice ("Calls may be recorded for quality and service improvement") if not already present.
  - Document retention policy (recommended 13 months, matching commerce limitation periods). Auto-delete after.
  - If Toky's retention is ~90 days, **our local copy becomes the system of record**.

---

## 3. Transcription Model Comparison (phone audio, 8 kHz)

| Model | Cost / min (batch) | Diarization | Streaming | Notes |
|---|---|---|---|---|
| **OpenAI Whisper** (`whisper-1`) | $0.006 | ❌ native (needs WhisperX / pyannote) | ❌ | Already integrated; no diarization = poor fit for 2-party sales |
| **Deepgram Nova-3** | $0.0043 batch / ~$0.0077 stream | ✅ built-in (+$0.001/min) | ✅ | Purpose-built for call centers. **Top pick.** |
| **AssemblyAI Universal-2** | $0.0025 | ✅ built-in (+$0.00033/min) | ✅ (Universal-3 Pro Streaming) | Strong on noisy/accented audio; Universal-3 Pro is telephony-tuned |
| **Google Chirp 2 / 3** | $0.016 | ✅ (extra) | ✅ | Most expensive; GCP lock-in |
| **Azure AI Speech** | ~$0.012–0.017 | ✅ | ✅ | Heavy onboarding; overkill for single-tenant |
| **ElevenLabs Scribe v2** | $0.0067 ($0.40/hr) | ✅ up to 48 speakers | ✅ 150 ms | Best for broadcast/interviews; not telephony-tuned |

### Top picks
- **(a) Batch historical backfill → Deepgram Nova-3 (batch).** Cheapest with built-in diarization, explicitly phone-tuned. ~$0.005/min all-in.
- **(b) Real-time per-call → Deepgram Nova-3 async REST.** Call has ended — no streaming needed. POST the mp3 URL, transcript back in ~5–15s for a 5-min call. AssemblyAI is a close second.

Keep Whisper for the **existing** consultation-dictate flow. All Toky audio goes to Deepgram.

**Sources:** [Deepgram pricing](https://deepgram.com/pricing), [Deepgram Nova-3 blog](https://deepgram.com/learn/introducing-nova-3-speech-to-text-api), [Deepgram best-of 2026](https://deepgram.com/learn/best-speech-to-text-apis-2026), [AssemblyAI pricing](https://www.assemblyai.com/pricing), [Whisper telephony discussion](https://community.openai.com/t/best-solution-for-whisper-diarization-speaker-labeling/505922), [ElevenLabs Scribe](https://elevenlabs.io/speech-to-text), [Google STT pricing](https://cloud.google.com/speech-to-text/pricing), [Artificial Analysis STT benchmarks](https://artificialanalysis.ai/speech-to-text/models/whisper).

---

## 4. LLM Selection

### 4.1 Analytic pattern-finding (long context matters)

| Model | Context | $/M in | $/M out | Notes |
|---|---|---|---|---|
| **Claude Opus 4.7** | 1M | $5 | $25 | Top reasoning (94.2% GPQA); best at nuanced sales-call patterns. **Top pick.** |
| Gemini 2.5 / 3.1 Pro | 2M | $1.25–$2 | higher | 60% cheaper; bigger context. Strong fallback / pre-filter pass. |
| GPT-4.1 / GPT-5.4 | 1M | mid | mid | Best web-research; lower on agentic tasks |

Per monthly run (ingest ~5M input tokens of transcripts, emit ~20K findings) with Opus 4.7 ≈ **$25.50**. Weekly or monthly cadence is trivial.

### 4.2 Per-call structured extraction (cheap + reliable JSON)

| Model | $/M in | $/M out | JSON/schema | Cost / call |
|---|---|---|---|---|
| **Claude Haiku 4.5** | $1.00 | $5.00 | Strong tool-use, 200K ctx, 90% prompt-cache discount | ~$0.008 (pre-cache) / **~$0.002 (post-cache)** |
| GPT-4o-mini | $0.15 | $0.60 | Native JSON mode | ~$0.0012 |
| GPT-5.4 Mini | $0.25 | $2 | Best-in-class schema reliability | ~$0.002 |
| Gemini 2.5 Flash | $0.30 | $2.50 | 1M context, cheap | ~$0.003 |

**Recommendation:** Claude Haiku 4.5 as primary. Rationale:
1. Existing backend is all-OpenAI — diversifying hedges against OpenAI outages on the real-time path.
2. 90% prompt-cache discount on the pricing catalog (same on every call) makes repeat extractions nearly free.
3. Tool-use JSON schema enforcement is solid for this model class.

**Fallback:** `gpt-4o-mini` (already wired in `ai_service.py`) — zero new deps if we want the fastest MVP.

**Sources:** [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Claude Haiku 4.5](https://www.anthropic.com/claude/haiku), [LLM pricing comparison 2026](https://intuitionlabs.ai/articles/ai-api-pricing-comparison-grok-gemini-openai-claude).

---

## 5. Proposed Architecture

### 5.1 Real-time path (Workstream B)

```
Toky call ends
   │
   ▼
Toky webhook (inbound/outbound_call_ended)
   │   payload: {callid, direction, agent, numbers, duration, record_url, …}
   ▼
FastHTML endpoint: POST /toky/webhook            [as_webapp on m4]
   │  - verify source IP (+ HMAC once Toky confirms)
   │  - insert CDR row into toky_calls (idempotent on callid)
   │  - 200 OK immediately
   │  - enqueue job
   ▼
Worker (asyncio task or separate process on m4)
   │  1. download record_url → audio_store/{callid}.mp3
   │  2. POST to Deepgram Nova-3 (prerecorded, diarize=true, model=nova-3-general)
   │  3. store transcript JSON → audio_store/{callid}.transcript.json
   │  4. call Claude Haiku 4.5 with:
   │        - system prompt + pricing catalog (prompt-cached)
   │        - transcript
   │        - tool schema: {staging_project, quote_items[], cs_task | null, call_classification}
   │  5. write local SQLite:
   │        - staging_project_drafts
   │        - quote_drafts  (linked to project)
   │        - cs_tasks       (linked to project, only if applicable)
   │  6. push notification → existing AS mobile apps (iOS/Android) + Telegram
   ▼
Human review in portal / mobile app → approve / edit → push to Zoho Staging_Report
```

### 5.2 Historical backfill (Workstream A)

```
One-shot Python script: tools/toky_backfill.py
   - paginate /cdrs/by-date earliest → today (500/page, 100 ms throttle)
   - per CDR: GET /recordings/{callid}, download mp3
   - batch Deepgram (async REST, 20 in flight)
   - store transcripts in toky_transcripts
   - (optional) Haiku extraction to populate staging_project_drafts

Then: analytics/toky_insights.py
   - bundle transcripts (respect 1M Opus context) → Claude Opus 4.7
   - prompts: win/loss wording, objection taxonomy, agent scorecards, call length vs conversion
   - write to analytics_reports + markdown export
```

### 5.3 Integration with existing Astra backend

- **Read-only from Zoho Staging_Report** — use existing sync pattern (`as_webapp/zoho_sync.db`, authoritative on m4 per `MEMORY.md`). Match Toky caller phone numbers → existing Zoho contacts where possible.
- **New authoritative local tables** (m4 SQLite):
  - `toky_calls` (CDR mirror, PK = callid)
  - `toky_transcripts` (callid PK, deepgram_json, extracted_at)
  - `staging_project_drafts` (links to zoho_contact_id if matched)
  - `quote_drafts` (line items refs existing pricing catalog)
  - `cs_tasks` (links to existing TaskBoard — `as_android/.../taskboard/`, `as_ios/.../TaskBoardView.swift`)
  - `analytics_reports`
- **Reuse** `ai_service.py` pattern; add `toky_service.py` alongside.
- Expose in mobile apps via a new "Call Intake" tab; approvals push to Zoho via the existing writeback path.

---

## 6. Cost Estimate

**Assumption (flagged):** 30 calls/day × 5 min avg × 30 days = **4,500 min/month**. ~10,000 historical calls × 5 min = **50,000 min backfill**.

### Monthly steady-state (Workstream B)
| Line item | Unit cost | Volume | Monthly |
|---|---|---|---|
| Deepgram Nova-3 batch + diarization | $0.005/min | 4,500 min | **$22.50** |
| Claude Haiku 4.5 extraction (cached catalog) | ~$0.002/call | 900 calls | **$1.80** |
| OpenAI embedding (optional, semantic search) | ~$0.02/M tok | ~5M tok | **$0.10** |
| Claude Opus 4.7 monthly analytics roll-up | ~$25/run | 1/mo | **$25.00** |
| **Total** | | | **~$50 / month** |

### Historical backfill (Workstream A, one-shot)
| Line item | Unit cost | Volume | One-shot |
|---|---|---|---|
| Deepgram Nova-3 batch + diarization | $0.005/min | 50,000 min | **$250** |
| Claude Haiku 4.5 extraction | ~$0.002/call | 10,000 | **$20** |
| Claude Opus 4.7 initial deep analysis (5 targeted runs) | ~$25/run | 5 | **$125** |
| **Total** | | | **~$395** |

Even at 10× volume the API bill stays under $500/month. The real cost is engineering time (see §7).

---

## 7. Implementation Phases (2-week chunks)

### Phase 0 — Pre-work (3 days)
- Generate Toky API key; confirm `X-Toky-Key` against `/cdrs` sandbox.
- Request from Toky support: **(a)** webhook HMAC scheme, **(b)** recording retention period, **(c)** webhook source IPs.
- Add IVR consent notice if missing.
- Fund Deepgram + Anthropic accounts ($50 each).

### Phase 1 — MVP real-time (weeks 1–2)  ◀ **minimum viable first cut**
- New SQLite tables + migrations on m4.
- `POST /toky/webhook` endpoint with IP-allowlist verification.
- Worker: download → Deepgram → Haiku extraction → write `staging_project_drafts` + `quote_drafts`.
- Simple review UI in existing portal: list drafts, one-click accept/edit.
- Telegram notification on new draft.

### Phase 2 — Backfill (weeks 3–4)
- `tools/toky_backfill.py` with pagination, throttling, resume-on-crash.
- Run across ~10k calls; populate `toky_transcripts`.
- Dedup-match to Zoho projects by phone + date.

### Phase 3 — Analytics (weeks 5–6)
- `analytics/toky_insights.py` with Claude Opus 4.7.
- Pre-defined reports: win/loss wording, objection taxonomy, agent scorecard, call-length vs conversion.
- Monthly cron; results rendered in portal.

### Phase 4 — Nice-to-haves (weeks 7–8+)
- CS-task auto-creation with smart routing.
- Quote auto-send for customer confirmation (human-approved only).
- Semantic search over transcripts (embeddings + local vector store).
- Live call "next-best-action" coaching (requires Toky streaming; future).
- Webhook HMAC signing once Toky exposes it.

**Minimum viable first cut = Phase 1 only.** Everything after is additive.

---

## 8. Risks & Open Questions

1. **Toky webhook signing is undocumented.** Rely on IP allowlisting until confirmed.
2. **Recording retention period is undocumented** — treat as ~90 days; run backfill ASAP.
3. **Diarization accuracy on Astra's actual audio** is unknown. Budget a 1-day spike: 20 real Toky mp3s through Deepgram and Whisper-diarize side by side; pick winner on measured WER.
4. **Haiku 4.5 JSON reliability** on our schema — validate on 50 calls pre-launch; fall back to `gpt-4o-mini` if strict-schema failures exceed ~2%.
5. **PIPEDA compliance** — explicit recording notice + 13-month retention policy written up before backfill ingests anything.
6. **Zoho writeback** stays manual approval. Never auto-mutate Zoho from an LLM draft.

---

## 9. Sources

**Toky API:** developer.toky.co (reference + docs pages listed in §2), docs.bird.com (Toky acquisition)
**Transcription:** deepgram.com/pricing & /learn, assemblyai.com/pricing, cloud.google.com/speech-to-text/pricing, elevenlabs.io/speech-to-text, artificialanalysis.ai/speech-to-text
**LLMs:** platform.claude.com/docs/en/about-claude/pricing, anthropic.com/claude/haiku, intuitionlabs.ai/articles/ai-api-pricing-comparison-grok-gemini-openai-claude
**Compliance:** priv.gc.ca (PIPEDA), network-telecom.com (Ontario recording), recordinglaw.com (Canada)

**Existing code referenced:**
- `as_webapp/as_portal_api/ai_service.py` (current Whisper + gpt-4o-mini integration to extend)
- `as_webapp/as_portal_api/routes.py` (where new `/toky/webhook` endpoint will live)
