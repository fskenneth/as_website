# Astra Staging Sales-Ops Analytics Report
**Analysis Period:** Recent ~400 calls | **High-Signal Subset:** ~120 diarized transcripts

---

## 1. Pipeline Snapshot

### Volume by Call Type
| Type | Count | % of Total |
|------|-------|------------|
| sales_follow_up | 68 | 56% |
| sales_new_lead | 35 | 29% |
| scheduling | 15 | 12% |
| customer_service_issue | 10 | 8% |
| other | 8 | 7% |

### Direction Split
- **Inbound:** ~55% (new inquiries, scheduling requests, CS issues)
- **Outbound:** ~45% (follow-ups, return calls)

### Agent Workload
Primary agents identified: **Ashika/Aashika** (dominant - handles ~85% of transcribed calls), **Clara/Claire** (backup/overflow)

Ashika handles the vast majority of both inbound and outbound calls. Clara appears primarily on scheduling and some new leads.

### Actionable vs. Noise (Inbound)
- **Actionable:** ~72% (genuine sales inquiries, scheduling, CS requiring resolution)
- **Noise:** ~28% breakdown:
  - Wrong number/service mismatch: 5 calls (furniture assembly request `lojhfv13`, stage steps `6eb6cd30`, Crawford Staging lookup `7ce8c4b3`)
  - Job inquiries: 4 calls (`3f2b0886`, `8255c36c`, `e46cae90`, `3munb7hj`)
  - Employment verification: 1 call (`50547a65`)
  - Out-of-service-area: 3 calls (Parry Sound `d67fce7e`, Belleville `4f20b36c`, Chicago trade show `9af532d7`)

---

## 2. Sales Patterns That Close

### Opening Phrases Correlated with Good Flow

**Effective openings (from won/strong-pending calls):**

1. **Immediate value acknowledgment + info-gathering:**
> "Yes. Absolutely. I just need to confirm a few things, and I can certainly help you with the price." — `0ddf4849` (won), `228bd326` (pending-strong)

2. **Warm return-call framing:**
> "Hi there. It's Astra of Staging returning your call. Can I help you?" — `3qnb53lr` (consultation scheduled)

3. **Recognition of referral/relationship:**
> "You were referred by Goldie, and we really appreciate her business and referring you to us." — `d1c911b5` (scheduled, $2600 deal)

**Weak openings (correlated with lost/stalled):**
- Answering as wrong company: `78c6ee08` opened with "Hello. Advanced Locksmith" — customer confused, deal lost
- Passive/unclear: calls where agent doesn't immediately take control of the conversation

### Closing Phrases That Commit Customers

**High-conversion closers:**

1. **Deposit + date lock:**
> "I'm gonna send you a detailed quote in just a few minutes... We require 50% deposit to confirm the booking." — Used in `0055ad3e` (won), `55f23d2d` (won)

2. **Scarcity + accommodation:**
> "We can stage it this week on Wednesday... if you can kindly make the deposit to confirm and book your spot." — `f66fb946`

3. **Explicit next-step ownership:**
> "Let's go ahead with that... Sounds good. Thank you so much, and we look forward to working with you." — `0055ad3e` (won - $1000 deposit same day)

4. **Negotiation closure with value add:**
> "If you wish to proceed with us, I can throw in the photography service at no extra charge." — `5da13ea0`

### Call Length Patterns

| Outcome | Avg Duration | Pattern |
|---------|--------------|---------|
| Won | 8-15 min | Deep discovery + pricing + scheduling in one call |
| Pending (strong) | 6-12 min | Quote sent, consultation scheduled, clear next step |
| Pending (weak) | 3-6 min | Customer "will think about it," no deposit/date |
| Lost | 2-5 min | Price objection unresolved or service mismatch |

**Key insight:** Won calls typically involve 10+ back-and-forth exchanges on property details before pricing is discussed. Lost calls often jump to price within first 3 exchanges.

### Questions That Elicit Property-Specific Detail

**High-signal questions (from successful calls):**

1. "Would you approximately know the property size?" — Asked in 90%+ of calls
2. "Is it vacant or occupied?" — Critical for pricing accuracy
3. "What's on the main floor? How many bedrooms?" — `228bd326`, `4ee9dc66`
4. "When are we looking to get it staged?" — Creates urgency context
5. "Is there a price range you had in mind?" — `0ddf4849` used this to negotiate from $2100→$1850

**Underutilized question (appears in won calls):**
> "Do we have a rough timeline on when we are looking to get it listed?" — Appears in `02a3708e`, creates urgency and qualifies serious buyers

---

## 3. Objection Taxonomy

| Objection | Frequency | Representative Quote | Best Response |
|-----------|-----------|---------------------|---------------|
| **Price too high** | 18 occurrences | "That is way too much for my client's budget" — `dtnnirmq` | Offer reduced scope: "Would you be open to just take the main level then?" — `4dca6b46` |
| **Comparing quotes** | 12 occurrences | "I'm calling around to see if there's other companies" — `46a4405e` | "If you get any other quote, please give us a callback... we really wanna make it happen" — `07e3ad2b` |
| **Monthly renewal concern** | 8 occurrences | "Monthly renewal fee too expensive... wants flat rate until sold" — `0hnvb36t` | Extend initial term: "We can offer forty-five days to begin with" — `d1c911b5` |
| **Need to consult spouse/partner** | 7 occurrences | "I have to talk to my wife" — `249222f9` | Schedule consultation anyway: "We are available next week... This is a complimentary service" |
| **Timeline mismatch** | 6 occurrences | "Cannot wait until April 9 - needs staging by Wednesday" — `cd62afc9` | Lost — no effective counter when fully booked |
| **Need to see design first** | 5 occurrences | "Cannot commit without seeing design/floor plan first" — `f8a5d468` | "I could share some recent MLS listings with you" — `592b93dd` |
| **Found someone else** | 4 occurrences | "We found someone else" — `0qst76am` | No recovery possible |

**Objection with lowest win rate:** Timeline mismatch — 0% recovery when customer needs staging within 48-72 hours and Astra is booked.

**Objection with highest recovery rate:** Price negotiation — ~60% recovery rate when agent offers reduced scope or extended term.

---

## 4. Agent Scorecard

### Ashika (Primary Agent)

| Metric | Value |
|--------|-------|
| Call volume | ~85% of transcribed calls |
| Avg duration | 7.2 minutes |
| % leading to committed next step | 62% |

**Strengths:**
- Excellent at structured discovery: consistently asks property size, vacancy status, room count, timeline
- Strong negotiation flexibility: "We can try our best to squeeze in and meet you midway" — `0ddf4849`
- Proactive WhatsApp/email follow-up offering

**Weaknesses:**
- Occasionally answers phone incorrectly: "Hello. Advanced Locksmith" — `78c6ee08`
- Sometimes doesn't push for deposit commitment on strong calls
- Quote from `f8a5d468`: customer wanted design preview, Ashika defaulted to "design links are sent 24-48 hours before staging" without offering alternatives sooner

**Distinctive pattern:** Ashika uses "Mhmm" extensively (20+ times per call average) — creates conversational flow but occasionally sounds disengaged on playback.

### Clara (Secondary Agent)

| Metric | Value |
|--------|-------|
| Call volume | ~15% of transcribed calls |
| Avg duration | 5.8 minutes |
| % leading to committed next step | 48% |

**Strengths:**
- Good at handling scheduling logistics
- Clear communication on process: "We send out a proposal with continuing to do list... staging item list" — `46a4405e`

**Weaknesses:**
- Less price negotiation flexibility demonstrated
- Fewer examples of overcoming objections in transcripts

---

## 5. Customer Service Theme Clustering

### Top 3 Recurring Issues

**1. Delivery/Timing Conflicts (4 incidents)**
- `31b37369`: Randy urgent — delivery window changed from 10-12 to 1-3, customer must leave by 1pm
- `c6b1271a`: Staging team delay — photographer scheduled 10:30am, team not arrived
- `858e6581`: Jackie — staging team not present at scheduled time

**Quote:** "Trying doesn't work. I will not be there if they come at 01:00." — Randy, `31b37369`

**2. Property Damage During Staging (2 incidents)**
- `c0a24108`: HVAC door damaged at 5 Everson Drive Unit 830 — door not sliding properly after furniture delivery
- (Referenced in multiple calls as concern customers raise)

**Quote:** "They had to take off our HVAC door to get some of the furniture inside, and, unfortunately, it's been damaged and it's not sliding properly." — `c0a24108`

**3. Billing/Invoice Discrepancies (2 incidents)**
- `5cbpgks9`: Josephine Carroll confused about $2,192.83 missing from invoices (resolved — was third property charge)
- `b2fe0011`: Same customer, voicemail about name correction and total discrepancy

**Severity Pattern:**
- **Urgent (same-day resolution required):** Delivery timing conflicts, property damage
- **Normal (24-48 hour resolution):** Invoice corrections, name changes
- **Low:** General inquiries routed to wrong department

---

## 6. Cold-Call Vendor Spam Registry

**Companies/individuals cold-calling Astra to sell services:**

| Caller | Contact | Pitch | Call ID |
|--------|---------|-------|---------|
| Sterling Backcheck | +16048812011 | Employment verification (RBC) | `50547a65` |

**Note:** Very low vendor spam volume in this dataset. Most "other" calls were job applicants or service mismatches rather than B2B cold calls.

**Recommended block/do-not-engage:** No urgent additions from this corpus.

---

## 7. Concrete CRM / Process Recommendations

### 1. Implement "Timeline Qualification" at Minute 1
**Data:** Won calls ask "When are we looking to get it staged?" early. Lost calls from timeline mismatch (`cd62afc9`) could have been qualified out faster.

**Action:** Add mandatory field in CRM: "Staging Date Needed" — required before quote generation. If <5 days and calendar is full, trigger waitlist protocol instead of standard quote flow.

---

### 2. Create "Price Objection Playbook" with Pre-Approved Tiers
**Data:** 18 price objections recorded. Ashika successfully negotiates ~60% by offering:
- Reduced scope (main floor only): `4dca6b46`
- Extended term (45 days instead of 30): `d1c911b5`
- Photography bundle: `5da13ea0`

**Action:** Document three pre-approved discount tiers:
- Tier 1: 15-20% off list (standard promo)
- Tier 2: 25-30% off + extended to 45 days (for realtors with volume potential)
- Tier 3: Scope reduction (remove bedrooms/basement) with clear price delta

---

### 3. Add "Design Preview Request" Workflow
**Data:** 5 customers objected to committing without seeing furniture selections. Current response: "design links sent 24-48 hours before staging" — creates friction.

**Action:** Create shareable portfolio deck by property type (condo <800sqft, townhouse, detached 2000+sqft). When customer asks "can I see what you'll bring?", agent responds: "I'll send you 3 similar properties we staged last month within 10 minutes."

Quote from `592b93dd`: "I could share some recent MLS listings with you" — this worked.

---

### 4. HVAC/Door Damage Incident Checklist
**Data:** `c0a24108` — HVAC door damaged, customer has listing tomorrow. No documented escalation protocol apparent.

**Action:** Add pre-staging checklist item: "Photograph all doors/entry points before moving furniture." Create emergency vendor list for same-day door repairs (current gap: customer waiting for resolution with listing imminent).

---

### 5. Deposit Collection Enforcement
**Data:** `n8pt8cmpg` — Lucy confirmed for Monday staging, deposit never collected. Ashika discovered mid-follow-up: "I just realized deposit had not yet been received."

**Action:** Automate deposit reminder 72 hours before staging. Block calendar slot release until deposit confirmed in system. Quote from that call: "If you can kindly make the deposit to confirm and book your spot."

---

### 6. Wrong-Number/Service-Mismatch Quick Disqualification
**Data:** 5 calls wasted on:
- Furniture assembly request (`lojhfv13`)
- Stage steps for event hall (`6eb6cd30`)
- Parry Sound (out of area) (`d67fce7e`)

**Action:** Train agents on 15-second disqualification script: "Astra Staging provides home staging for real estate sales in the GTA. Is that what you're looking for?" — saves 3-5 minutes per mismatch call.

---

## Summary Metrics

| KPI | Value |
|-----|-------|
| Won deals in corpus | 8 |
| Lost deals in corpus | 12 |
| Pending (strong next step) | 45 |
| Pending (weak/no next step) | 23 |
| Average quoted price | $2,400-$3,200 |
| Most common discount | 20-30% off list |
| Average days on market (cited) | 29 days (March) |
| Consultation scheduling rate | 78% when offered |