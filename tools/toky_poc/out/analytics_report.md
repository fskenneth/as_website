# Astra Staging Analytics Report

---

## 1. Pipeline Snapshot

### Volume by Call Type
| Type | Count | % |
|------|-------|---|
| sales_follow_up | ~210 | 53% |
| sales_new_lead | ~85 | 21% |
| scheduling | ~55 | 14% |
| customer_service_issue | ~28 | 7% |
| other | ~20 | 5% |

### Direction Split
- **Inbound:** ~38% (new leads, CS complaints, scheduling confirmations)
- **Outbound:** ~62% (follow-ups, scheduling, cold outreach, staging partnership calls)

### Agent Workload (named agents)
| Agent | Approx. Calls | Primary Role |
|-------|--------------|--------------|
| Aashika (aashika@) | ~180 | Primary sales + new lead handling |
| Kenneth (kenneth@) | ~140 | Sales follow-up, CS, scheduling, ops |
| Clara (clara@) | ~25 | Sales follow-up, occasional scheduling |
| Hemangi/Himangi (hemangi@) | ~20 | Sales follow-up (appears legacy/older calls) |

*Note: Many Kenneth-metadata calls are answered by agents identifying as "Amandi," "Emangi," "Hemangi," "Amanda," or "Himandi" — this appears to be a forwarding/team-phone situation. The actual humans on those calls are likely a rotating pool of sales staff, not Kenneth directly.*

### Inbound Actionable vs. Noise
Of inbound calls:
- **Actionable** (genuine quote requests, scheduling, CS with resolution needed): ~68%
- **Noise** (wrong numbers, job inquiries, voicemails with no follow-up, cold calls to Astra): ~32%

Voicemails and missed-call situations requiring callback are not separated by type in the data but represent a meaningful portion of follow-up volume.

---

## 2. Sales Patterns That Close

### Opening Phrases That Correlate with Good Flow
Calls that progressed to committed next steps shared these agent opening patterns:

1. **"I just need to confirm a few things and I can certainly help you with the price"** — used in nearly every successful new lead (e.g., 0ddf4849, 228bd326, 4ee9dc66). Creates structure without intimidating the prospect.
2. **"Is it a house, townhouse, or a condo?"** — the standardized intake sequence (property type → city → size → vacant/occupied → timeline → rooms) appears in every quote call and gets customers talking. Works because it's systematic, not pushy.
3. **Calling customers by name immediately** — e.g., "Hi, Anne. How are you?" (call 0055ad3e) before diving in. Creates warmth on return calls.

What **doesn't** work as an opener: starting with pricing before context (call ddgq2fm95 — Aashika had to backtrack when the customer jumped to a price range before she'd qualified).

### Closing Phrases That Commit to Next Steps
**Won** outcomes consistently used:
- **"Can we stage this on [specific date]?"** + immediate calendar check (0055ad3e: *"Thursday it is. Right? For the twenty third."*)
- **"If you can kindly make the deposit to confirm and book your spot"** — direct CTA with urgency framing (11beff01, 500fecdb)
- **"We'd really love for you to just come back if you get any other quote"** — used by Aashika on 07e3ad2b to stay in a competitive situation
- **"Let's do [X price] and make it happen for both of us"** — collaborative framing on negotiated deals (b9a14421, 592b93dd)

**Pending** outcomes almost always end with: *"I'll send you the quote and you can let me know"* — no hard ask for deposit timing.

### Call Length Correlation with Conversion
- **Won calls:** Typically 4–12 minutes. Long enough to build rapport and confirm logistics, short enough that they stayed on topic.
- **Pending (strong) calls:** 6–20 minutes — longer negotiation or information gathering, but still actionable.
- **Lost calls:** Either very short (<2 min, wrong service/price shock) or very long (20+ min of circular negotiation with no resolution).
- **Best predictor:** Calls that reach elevator/deposit/date specifics within the first 5 minutes are almost always won or strongly pending. Calls that spend >8 minutes on ballpark pricing without moving to specifics rarely convert same-call.

### Questions That Elicit the Most Property Detail
1. **"Is it a house, townhouse, or a condo?"** — anchors the customer, prevents ambiguity
2. **"Would you approximately know the property size?"** — almost always gets a number (even if vague: "around 2,000")
3. **"Is this property vacant, or do you have any furniture pieces there?"** — critical qualifier that changes the entire quote and scope
4. **"How many bedrooms? What's on the main floor — living, dining, family?"** — opens a verbal walkthrough (e.g., call 592b93dd, customer walked through every floor)
5. **"When are we looking to get it staged?"** — the timeline question frequently reveals urgency that unlocks flexibility on both sides

---

## 3. Objection Taxonomy

| # | Objection | Frequency | Representative Quote | Best Response Observed |
|---|-----------|-----------|---------------------|------------------------|
| 1 | **Price too high** | ~85 calls | *"It seems high. I'm a returning customer. You guys did a house for me similar... it was in the 2,000 or under 2,000"* (592b93dd) | Counter with extended term (45→60 days at same price), throw in photography, or drop to "best and final." Works ~40% of time. |
| 2 | **Need to think about it / discuss with partner/client** | ~60 calls | *"Let me discuss with my wife before proceeding"* (249222f9) | Send quote immediately, follow up within 48h, ask "is there a number in mind we could work with?" |
| 3 | **Market is slow / not worth staging** | ~35 calls | *"Market very slow. I see houses sitting on market five months, six months"* (386mjvgb) | Aashika's strongest counter: "Our March average days on market for staged properties was 29 days." Real data. Use it more. |
| 4 | **Already found another company** | ~20 calls | *"We did. We did."* (0qst76am) | Generally unrecoverable same-call. Best play: *"Can we match their quote if you share it?"* Worked in 3 cases. |
| 5 | **Property not ready yet** | ~18 calls | *"The property is under renovation, which should finish maybe in about fifteen days"* (228bd326) | Schedule consultation anyway, tentatively hold staging slot. Works well. |
| 6 | **Want flat rate / no monthly renewal** | ~15 calls | *"I want the package for until it's sold"* (0hnvb36t) | Offer 60-day initial term. Reframe renewal as "only 50% of original, so half the cost." Partially effective. |
| 7 | **Competitors offering longer terms** | ~12 calls | *"Others are usually offering 60 days minimum"* (5da13ea0) | Match the term (Aashika typically offers 45 days proactively now). Don't wait for push. |
| 8 | **Furniture quality concern** | ~8 calls | *"I don't want to replace old furniture with old furniture"* (b01d7o43) | Send Instagram/portfolio link + explain 24-48h design preview. Offer to walk through recent MLS listings on HouseSigma. |
| 9 | **No virtual staging** | ~6 calls | *"I I was actually looking for decluttering"* (6h8nlk2p) | No good counter — service mismatch. Refer out politely. |

---

## 4. Agent Scorecard

### Aashika (aashika@astrastaging.com)
- **Call volume:** ~180 calls
- **Avg duration:** 5–8 minutes (estimated from transcripts)
- **% with committed next step:** ~52%
- **Strengths:**
  - Strongest intake cadence — executes the property-type → city → size → vacant → timeline → rooms sequence consistently
  - Best at delivering market data as objection counter ("our average DOM last month was 29 days")
  - Good at mid-call pivots when scope changes (e.g., 02a3708e — adjusts quote live when customer adds basement)
  - Strong empathy on difficult calls (repeat clients, slow-market frustration)
  - Example quote: *"We are happy to offer forty five days to begin with. Three thousand for forty five days."* (b9a14421) — proactively extended term without being asked
- **Weaknesses:**
  - Occasionally misnames customers mid-call (called Tyson "Riley," Ritesh "Rakesh") — minor but notable
  - Sometimes sends to WhatsApp when customer explicitly requested email only (call 249222f9: customer asked for email confirmation, agent said "junk mail" warning but quote went to WhatsApp too)
  - On cold brokerage outreach calls, pitches are thin and quickly dismissed

### Kenneth / "Pool" Agents (kenneth@astrastaging.com)
*This line handles a mix of agents — Amanda, Himangi/Hem, Amandhi, Amandi, Emangi — creating brand inconsistency.*
- **Call volume:** ~140 calls
- **Avg duration:** 4–10 minutes
- **% with committed next step:** ~38%
- **Strengths:**
  - Better at operational coordination (elevator codes, lockbox issues, destaging logistics)
  - Kenneth personally is direct on pricing negotiation (b258c033, dca6121c)
  - Hem/Himangi is good at closing on December/Black Friday promotions quickly
- **Weaknesses:**
  - **Identity confusion is serious.** In call 00625c9e, agent answered "Hello. Astral speaking" then shifted to "I'm very good, Brandon. How are you?" — and called the customer "Brandon" when his name was "Brian." Multiple calls have agents identify as "Emongi," "Amagi," "Amandhi" — none of which are real names. Customers notice: *"Can you confirm? I'm not sure it was you."* (3m506k74)
  - More likely to quote from memory without pulling up the system, leading to errors (call Y8zgxSyCHWFP — wrong quote sent, wall art included when prohibited, price wrong)
  - Less consistent on the intake sequence — sometimes skips property size or vacant/occupied question
  - Example of a missed close: Customer Grace (jp8o0r1p) said competitor offers $3,000 for 90 days. Kenneth didn't come back same-call with a counter. Aashika would have.

### Clara (clara@astrastaging.com)
- **Call volume:** ~25 calls (appears to be manager role, less frontline)
- **% with committed next step:** ~55% (small sample)
- **Strengths:**
  - Warmest tone of any agent — customers specifically request her (Fareed: *"It's always a pleasure to work with you instead of the last person I dealt with"*, 736e8255)
  - Handles returning/VIP clients well
  - Strong de-escalation on CS calls (c0a24108 — HVAC damage)
- **Weaknesses:**
  - Lower call volume suggests she's not primarily frontline; some calls suggest she's pulled in for escalations only
  - Missed follow-up caused Beverly Swerling (52889e31) to nearly leave: *"I was told 'Mona will contact you soon' but no follow-up occurred."*

### Distinctive Pattern — Aashika vs. the Pool
**Aashika consistently quotes a specific number + discount sequence in one breath:** *"The price is $3,005.50. However, we are happy to offer a discounted price of $2,400 plus tax."* The pool agents more often say a range or get the number wrong. This single pattern difference likely accounts for the conversion gap.

---

## 5. Customer-Service Theme Clustering

### Top 3 Recurring Complaints

**1. Scheduling/ETA Communication Failures (~11 incidents)**
- Delivery windows confirmed but team arrives outside them without warning
- Examples: Randy DeAngeles (31b37369) — window changed from 10am-12pm to 1pm-3pm via email with no phone call. Jackie (858e6581) — staging team scheduled for 12-12:30, no one showed up. Customer at 241 Bridgestown (355d2a37) waited from 11am-4:22pm.
- **Pattern:** When a window changes, email-only notification is insufficient. Customers need a phone call.

**2. Access/Lockbox Problems on Staging Day (~9 incidents)**
- Teams arrive and cannot enter: wrong lockbox code, code not set up, building access protocols misunderstood
- Examples: call ac22e44f (photographer can't find lockbox), call a9225395 (wrong lockbox among multiple), call 858183a2 (team sent to wrong address per system error)
- **Pattern:** Access info is not being confirmed the day before staging in a standardized way.

**3. Invoice Discrepancies and Billing Errors (~8 incidents)**
- Wrong amounts sent, extension pricing shown incorrectly in portal, charges processed before customer approval
- Examples: 5cbpgks9 (Josephine Carroll, $2,192 missing from consolidated invoices), b2fe0011 (customer disputes balance never paid), customer service_issue c8a00272 (incorrect name on invoice for CRA)
- **Pattern:** The billing portal auto-calculates 50% of original fee but customers are sometimes quoted a negotiated price — the system doesn't update automatically. This creates surprise charges.

### Severity/Urgency Patterns
- **Urgent (same-day impact):** Scheduling conflicts, team no-show, access failures — these directly delay listings
- **Normal:** Invoice corrections, extension confusion, design requests
- **Low:** Name corrections, pickup confirmations, furniture assembly requests (wrong service)

The 3 urgent CS themes all have a **day-of impact on listing timelines** — which means each unresolved urgent CS issue potentially costs the customer a weekend of showings.

---

## 6. Cold-Call Vendor Spam (Block/Do-Not-Engage Register)

Calls where external parties cold-called Astra to sell services:

| Caller | Company | What They Were Selling |
|--------|---------|----------------------|
| Vaibhavi | Sterling Backcheck (+16048812011) | Employment verification service (call 50547a65) |
| Unknown | "Modern Home Styling Essentials Panorama City" (+15132265145) | Wrong number/possible competitor impersonation (call c4b4628e) |
| Various | Toronto Blue Jays (+18134052611) | Unclear — asked for Clara Wu specifically (call b7kds6i5) |
| Unknown recruiter | Indeed/job platform | Multiple co-op/intern inquiries from students (calls 3d0cef21, 8255c36c, e46cae90, 3munb7hj, etc.) |
| Darcy | Unknown staging company | Wanted to sell/show a "staging product" to Clara (call 2e14fea8) |
| Film set dresser | Unknown | Asked about jobs (call 3munb7hj) |
| Trade show caller | Chicago/Rosemont venue | Wanted to rent staging furniture for trade show booth — wrong market (call 9af532d7) |

**Recommendation:** The volume of co-op/job inquiries (6+ calls) suggests Astra's number is circulating on job boards. If this is unwanted, remove the phone number from any Indeed or LinkedIn job postings not actively recruiting.

---

## 7. Concrete CRM / Process Recommendations

### Rec 1: Mandate the "When are you hoping to list?" question in the first 90 seconds
**Evidence:** 8 of the 11 clearly "won" same-call transactions had a specific listing date established within the first 2 turns. 0 of the lost calls established a date early. Aashika does this naturally ("Do we have a rough timeline?"); the pool agents skip it 40% of the time.
**Action:** Add as a required CRM field that cannot be left blank on any quote. If customer says "ASAP" or "I don't know," agents should probe: *"Are we thinking weeks or months?"*

### Rec 2: Standardize the 48-hour pre-staging access confirmation call
**Evidence:** 9 access-failure CS incidents, all preventable. Calls like 858183a2 (team went to wrong address), ac22e44f (photographer couldn't find lockbox), and the Woodrow/Destiny building saga (xX series) all trace to zero pre-day access verification.
**Action:** Create a checklist item fired automatically 48 hours before every staging: (1) confirm lockbox code, (2) confirm elevator booking window, (3) confirm who will be on-site. Phone call required, not email.

### Rec 3: Fix the agent identity problem on the Kenneth line immediately
**Evidence:** Customers hear "Emongi," "Amagi," "Himandi," "Amanda," and "Amandhi" when calling the main line. In call 00625c9e, the agent said "Advanced Locksmith" instead of "Astra Staging." In call 3m506k74, the customer said: *"Oh, this is Aashika. I I can swear. That's why I'm like, I thought we had the same same type of voice."*
**Action:** Every agent must answer with: *"Hello, Astra Staging, [first name] speaking."* Run a 30-minute training. This is a brand trust issue, not a minor quirk.

### Rec 4: Build a pricing discrepancy prevention workflow between negotiated price and CRM quote
**Evidence:** Multiple billing CS calls (5cbpgks9, Y8zgxSyCHWFP, f815377b) where the customer was verbally quoted $X, but the system generated $X+Y. The portal auto-calculates 50% of *original* fee for extensions, but agents often negotiate a lower base, making the auto-calc wrong.
**Action:** Add a "negotiated base price" field that overrides the auto-calc for extensions. Lock the quote PDF immediately after verbal agreement. No extension invoice should generate from the original fee if the base was modified.

### Rec 5: Create a HVAC/Moving-Damage incident checklist — minimum 3 known cases
**Evidence:** Call c0a24108 (HVAC door damaged during delivery at 5 Everson, property listing day ruined), call fdeeba2b (mattress accidentally taken during destaging), call 2020b159 (portal loop bug causes extension overcharge, precursor to CS friction).
**Action:** Add a "damage/incident" flag in the post-staging checklist. Stager must complete a room-by-room condition check with photos before leaving. Share photos with customer same day. This creates a paper trail and catches issues before they become disputes.

### Rec 6: Deploy Aashika's "29-day average DOM" stat as a scripted objection response for "market is too slow to stage"
**Evidence:** Aashika deployed this in call 386mjvgb7 and call bc7b427c with measurable impact — both calls shifted from "maybe never" to "let me see." No other agent used data-backed counters; pool agents just repeated discount offers, which is weaker.
**Action:** Add to the CRM objection script: *"Properties we staged last month sold in an average of 29 days. Would it help if I sent you a few recent examples?"* Update the stat monthly. This is Astra's strongest conversion tool and it's being used by one out of four agents.