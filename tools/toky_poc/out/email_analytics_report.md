# Astra Staging — Email Analytics Report

---

## 1. Pipeline Snapshot

### Volume by Classification
| Class | Count (approx.) | Notes |
|---|---|---|
| `scheduling` | ~95 | Largest segment; mostly logistics/access/elevator coordination |
| `customer_service` | ~75 | Payments, complaints, receipts, completion acknowledgments |
| `quote_followup` | ~70 | Follow-up on sent quotes; many go silent |
| `customer_inquiry` | ~35 | New leads from web form + email |
| `vendor_or_3rd_party` | ~30 | Cold pitches, landlord, photography vendor deliveries |
| `quote_sent` | ~8 | Explicit quote-delivery emails |

### Inbound vs. Outbound Split
- **Inbound** (non-@astrastaging.com sender): ~55%
- **Outbound** (sender = @astrastaging.com or sales@): ~45%

Key outbound senders: `aashika@astrastaging.com` (primary), `mrunal@astrastaging.com` (collections/ops), `sales@astrastaging.com` (automated proposals/confirmations/read-receipts)

### Typical Lifecycle: Inquiry → Won Deal
**Minimum touchpoints observed on won deals:**
1. Inquiry (web form or email) → automated internal alert
2. Quote sent (same day or next day)
3. Customer asks clarifying question or confirms date → 1–2 emails
4. Deposit confirmed → booking locked → scheduling thread (3–6 more emails on condos, fewer on houses)
5. Staging day notification → pickup/destage (2–4 more emails)

**Rough email count per won deal: 8–15 emails** (condos with elevator logistics at higher end)

### Quote-Amount Distribution
| Metric | Amount |
|---|---|
| **Min observed** | $100 (7-day extension, Rebecca email 39399) |
| **Common small deposit** | $500 (condos/small properties) |
| **Median deposit** | ~$1,000–$1,500 |
| **Median full quote** | ~$1,800–$2,200 |
| **Notable high** | $4,500 + HST (117 Parkview Hill, email 38616) |
| **Max observed** | $7,833.73 total (92 Scenic Wood Cres, email 43077) |

---

## 2. Inquiry → Quote Conversion

### Questions in Inquiries That Correlate with Fast Quotes

**Signals that got quotes sent same-day or next-day:**
- Explicit property address provided upfront (emails 38782, 38802, 38295)
- Realtor identifies as agent (faster trust + urgency: emails 38750, 40950, 42126)
- "Stage ASAP" or "Stage in 1 Week" timing field (emails 38286, 40950, 43412)
- Photos/videos attached or offered immediately (emails 40458, 42071, 42556)
- Specific room list provided (email 38802: 10 areas listed; email 41553: 15-room breakdown)

**Signals that slow quote delivery:**
- "Stage after 1 Month" or vague timing → Aashika sometimes waits on photos
- Property in fringe geography (Angus, Collingwood, NJ) → "do you cover?" back-and-forth (emails 42069, 43492)
- Occupied homes needing photos/videos before quoting (emails 41574, 43488)

### Customer Attributes That Predict Quote Sent
1. **Realtor identity** — Realtors get quotes faster; owners get more qualification questions
2. **Referral source** — Referrals (Reza Afshar mention email 38332; Adolphe referral email 38681) → same-day response
3. **Urgency phrasing** — "Stage ASAP," "listing photos taken soon," "staging for this Thursday" → immediate response
4. **Vacant property** — Quoted faster than occupied (no photos needed for vacant)
5. **Specific closing/listing date** — e.g., "listing early May" (email 40988), "first week of June" → quote typically within hours

---

## 3. Quote Follow-Up Patterns

### How Long Until Follow-Up?
- **Standard cadence observed:** Quote sent Day 0; follow-up email Day 3–7 if no response
- **Longest gap before follow-up:** Elie Rizk (Ajax, email 40473) — quote sent March 26, follow-up May 14 (49 days!)
- **Batch follow-up day:** April 2, 2025 — Aashika sent ~20 follow-up emails in one session to all stale quotes (emails 37054–37074)
- **Read-receipt triggers immediate call:** Automated emails (39386, 40984, 40915) prompt phone call within minutes of quote opening

### Language That Gets Re-Engagement

**Phrases that generated deposit/booking (closing language):**
- "Are you still planning to move forward with our services? If so, do you anticipate you will be ready to list in April?" (emails 37060–37072) — generic but structured; generated responses from Peggy, Alexandra, HuiWang
- "A detailed quote was sent a few moments ago in a separate email. When are you looking to get it staged?" (email 41504) — direct, low friction
- "The earliest we can stage this is May 28. Kindly confirm if this date works for you." (email 40918) — scarcity + call-to-action
- "Okay, let's do it! Just to confirm, the stage date is May 16?" (email 39881) — confirming verbally agreed terms → deposit link attached → Sandra Charry paid same day

**Phrases associated with silence/loss:**
- "Let me know if you have any other questions" (generic sign-off) — appears on most of the 20+ stale quotes followed up April 2 that went nowhere
- "Hope you're doing well! I just wanted to follow up" (email 37054, 37056, etc.) — yielded mixed results; HuiWang (70 Heartfield) and Jennifer Bourikas (Hampton St) both declined after these
- Quote sent with no mention of staging availability date → customer defers

**Specific email pairs: close vs. silent**
- **Closes:** 39881 ("Okay let's do it!") + deposit link → Bassam paid. 40977 (Sandra: "Good afternoon Aashika I just made the $500 deposit") — quote same day, paid same afternoon.
- **Goes silent:** 37058 (Jakey, 1441 Danforth — "Hope you're doing well! Just follow up") — no response visible. 37073 (Florence, Oakville — same template) — no response.

---

## 4. Objection Taxonomy (Email-Side)

| Objection | Frequency | Representative Quote | Recovery Attempted? |
|---|---|---|---|
| **Price too high / competitor cheaper** | ~6 | "My local provider will do this house for $1,300" — Aaron Albright, email 39426 | Aashika held at $1,870; **LOST** |
| **Price too high vs. own budget** | ~5 | "Unfortunately your quote is quite high, I have $2200" — Ali Zamaniteam, email 40486 | Aashika tried callback; outcome unclear |
| **Price too high vs. comparable prior job** | 2 | "We did 40 Alder Rd with you…it was completely empty…almost the same price" — Adolphe, email 38596 | 5% discount → counter at $4,500 → **WON** (email 38616) |
| **Extension: want more days for same price** | ~4 | "They are only willing to extend if the price quoted ($1452.50) is for 60 days and not 30 days" — Michael Annan, email 40469 | Declined firmly; customer took pickup |
| **Extension: deferred payment request** | 2 | "We'd require at minimum 2 weeks to provide the extension payment" — Adolphe Khouri, email 41473 | Granted 2-week deferral → **Stayed** (email 41537) |
| **Scope unclear / items missing** | ~3 | "In the quote only 3 bedroom and living room" — Nikki Kha, email 42954 | Quote updated with/without basement options → **WON** (email 43425) |
| **Chose competitor (not price)** | 2 | "The other company's proposal better fits our needs" — Jeny/Ecko Jay, email 39946 | Graceful exit; no recovery |
| **Client decorating themselves** | 2 | "This client intends to decorate the house by themselves" — HuiWang, email 37033 | Acknowledged; no recovery |
| **Waiting for tenant/listing agreement** | 2 | "I've been dealing with a situation with the current tenant" — Alexandra Fantin, email 37024 | Patience → Fantin came back and booked (email 37691) |
| **Contract term confusion** | 2 | "How long is the contract for? Is it 5 week or 4 week?" — Erin Carlson, email 39366 | Clarified within hours; pending |
| **Portal/payment technical issue** | 3 | "The submit bottom doesn't work" — Guiti Zarif, email 40521; "Receipt page didn't show properly" — Sucharita, email 39403 | Resolved same day |
| **Wrong staging date sent by Astra** | 1 | "The staging is supposed to be tomorrow, not today" — Arpit, email 39327 | Internal error; corrected |
| **Physical damage to property** | 2 | "I had to invite the painter to repair the scuff marks that costed me more than 50 dollars" — Roy WU, email 39945 | $50 Tim Hortons gift card offered |
| **Staging items missing** | 2 | "The console table…was not placed…only one small [patio] set" — Muhammad Siddiqui, email 42543 | Replacement delivery scheduled Friday |
| **Terrace under-staged** | 1 | "A small 4 seat plus table was the only item provided [for 267 sq ft terrace]" — Michael Sistilli, email 43039 | Additional pieces + contract start date reset to June 26 |

---

## 5. Scheduling Friction

### What Scheduling Gets Stuck On

1. **Elevator booking at condos** — Most common friction point. Buildings require 2–5 days notice; Astra often requests same-day or next-day elevator slots. Examples:
   - 310-109 Front St: parking restriction 4–6pm caused 4 reschedule emails (39353–39374)
   - Grimsby (903-16 Concord): building needed "a few days notice"; moved Thursday → Friday (40452)
   - Mimico condo (Chantille): elevator check required before confirming date (38733)
   - 9 Tecumseth (Alexandra Fantin): elevator unavailable Friday → moved to Tuesday (43893)

2. **Astra-side schedule conflicts** — Astra internally reschedules customers with no advance notice:
   - Mike Savoy (13 Turnhouse): "There's been a small schedule conflict" → moved to 4–6pm (email 38604)
   - 80 Cocksfield (Fran): "Unfortunately there's been a schedule conflict for Monday 9-11am" → moved to 2–4pm (email 43053)

3. **Access code not provided upfront** — Requires a separate email:
   - 46 Benhurst Cres: Carl provided lockbox 0389 day-of (email 43507)
   - 2253 Glenfield Rd: Jeff provided lockbox 63801 day-of (email 44741)
   - 23 Huntingwood: Tricia provided code 1215 day-of (email 43388)

4. **Staging date error from Astra system** — Incorrect pickup date in automated email:
   - 1610-9225 Jane St: system showed Apr 30 but agreement was May 7 (email 39276)

5. **Weekend availability gap** — Astra doesn't stage weekends (Mon–Fri only):
   - Philip Leung requested June 28 (Saturday); Astra redirected to June 27 or 30 (email 41500)

6. **Balance payment required before pickup can proceed** — Multiple threads held up by unpaid balances before pickup date can be confirmed (Tanya Janic 310-109 Front, Chuka Etobicoke)

7. **Photographer timing** — Realtor books photographer same day as staging but Astra arrival window is unpredictable:
   - Jeff Mahannah (Oakville): photographer at 1pm; Astra arrived 10:30–11am (fine)
   - Todd Lister (Sycamore): photos at 4pm; Astra arrives 10am–12pm (fine)
   - Sophia Bailey (Minowan Miikan): original 12–12:30pm promise broken, arrived 1:30–2pm; elevator expires 3pm (email 40842) → **complaint**

### Patterns to Pre-Empt in Quote Email
- Ask for elevator booking window requirements at time of quote
- Confirm access method (lockbox vs. in-person) at quote stage
- State Mon–Fri availability clearly in the quote email
- Request payment settlement date commitment in the quote

---

## 6. Customer-Service Themes

### Top Recurring Complaints with Email IDs and Severity

| Complaint | Email IDs | Severity | Pattern |
|---|---|---|---|
| **Late arrival / broken time window** | 40842, 39230, 42055 | HIGH — first-time customer (Meghan McEvoy) said "I had to call Astra several times…kept changing" and flagged it publicly via email to sales@ | Condos, destaging; team apparently runs behind and doesn't proactively communicate |
| **Missing staging items** | 42543 (Muhammad: patio furniture), 36937 (Elaine: master lounge + accessories), 43039 (Michael: terrace) | HIGH — all required remediation visit | No pre-delivery checklist confirmation with client |
| **Price confusion after deposit** | 40869 (Poonam: $2450 → $2982.07) | MED — resolved by explanation (photography add-on) | Quote doesn't clearly itemize HST + photography add-ons |
| **Portal/receipt technical issues** | 40521 (Guiti: submit button broken), 39403 (Sucharita: receipt didn't display), 36981 (Frank Vella: click-to-pay broken) | MED | Zoho portal and Stripe receipt reliability |
| **Item accidentally taken during destaging** | 44687 (Joseph Awad: daughter's white duvet) | MED | Crew taking non-Astra items; requires return trip |
| **Wobbly furniture** | 42953 (Victor Alvarez: high table wobbly) | LOW | "Staging props are not for daily use" — response somewhat deflecting |
| **Scuff marks from movers** | 39945 (Roy WU: "had to invite painter") | MED — requested $50 compensation | Movers not careful with floors/walls |
| **Receipt format issues** | 40471 (Karen Bayer: "not in downloadable format"), 41572 (Joseph Awad: needs HST# for corporate billing) | LOW | Stripe receipts not meeting B2B invoice requirements |
| **Overdue balance collections** | 38772/38771/38775, 39392, 39250 | HIGH (cash flow risk) — Chuka went 4 reminders before paying; Antonio 3 reminders; Leanne 2 reminders; Tanya Janic ran out of money | Systemic pattern: balance due same day as staging, card on file declines |

### Patterns by Property Type or Season
- **Condos** generate disproportionate scheduling friction (elevator, parking restrictions, access codes)
- **Slow market Q1–Q2 2025** drove extension negotiation volume — multiple clients citing "current market conditions" when requesting deferred payment or free extensions (Adolphe, Aneri Brahmbhatt, Michael Annan, Shashank Saini)
- **Balance payment failures** visible across both house and condo segments — no seasonal pattern but correlated with higher-priced jobs ($1,700–$2,600 range where clients apparently don't budget for it)

---

## 7. Vendor / 3rd-Party Noise

**Do-Not-Engage Register:**

| Sender | Company | Email | Pitch |
|---|---|---|---|
| Frank | Guangzhou Jinyue Furniture | sales@jinyuefurniture.com | Wholesale furniture supplier, China |
| Chloe Wright | Gainsty | hello@engagementgainsty.com | Instagram follower growth |
| Andrew Moore | Gainsty | andrew@growmyig.com | Instagram follower growth (duplicate pitch) |
| Gabriel Perez | Gainsty | gabriel@iggainsty.com | Instagram follower growth (3rd pitch, same company) |
| Maushmi M S | Zoho Corp | maushmi.s@zohocorp.com | CRM webinar (CommandCenter 2.0) |
| Nowman | Zoho Corp | mohamednowman.n@zohocorp.com | Zoho FSM webinar |
| Naveen | Zoho Corp | naveen.tv@zohocorp.com | Zoho Projects conference |
| BOXABL | BOXABL | hello@boxabl.com | Investment solicitation (4+ emails) |
| Deborah Ross | Indaba Home Decor | deborah@indabatrading.com | Wholesale home decor supplier |
| Ammar Beg | HMH Construction | Ammar@hmhconstructioninc.com | Construction partnership pitch |
| Carmen Zong | Hans Real Estate Team | carmen@hansteam.ca | Event sponsorship ($500–$1,000) |
| Lisa Ormsby | OUR HOMES Media | lisa.ormsby@ourhomes.ca | Magazine ad space (2 solicitations) |
| Midhun Nair | Freight Sector Inc | midhun@freightsector.com | Freight/logistics services |
| G Noelle | The Designer's Domain | thedesignersdomain.membership@gmail.com | Promo bundle opportunity |
| Kashish Shah | Partridge Fine Landscapes | sales@partridgedesign.com | Snow management services |
| Ava Brown | GuestPostWolf | ava.brown@coloradonewstoday.com | Guest blog posts ($30/post) |
| Madison Calley | GuestPostMate | madison@guestpostmate.com | Guest blog posts |
| Emma | EP Social Studio | hello@epsocialstudio.com | Social media management |
| GSS Furniture | Get Set Style Furniture | info@getsetstylefurniture.com | Wholesale staging furniture |
| Sudan Movers | Sudan Movers | info@sudanmovers.com | Moving/staging logistics partnership |
| Midhun Nair | Freight Sector | midhun@freightsector.com | Freight services (follow-up) |
| Scott McGillivray | McGillivray Capital | invest@mcgillivraycapital.com | Real estate investment fund |
| Justin Bregman | Justin Bregman & Associates | info@justinbregman.com | Real estate newsletter (2x) |
| PTS | Portable Technology Solutions | info@ptshome.com | RFID software/hardware (3 emails) |
| Ora Flooring | Ora Flooring | oraflooring@gmail.com | Flooring wholesaler |
| Deborah Ross | Indaba Home Decor | deborah@indabatrading.com | Wholesale decor |
| Agua Canada | Agua Canada | info@aguacanada.com | Shower products marketing |
| Bay Street Integrity Realty | Bay Street Integrity Realty | info@baystreetintegrity.com | Selling surplus staging items |
| Brittney Mowat | Job applicant | bmowat28@gmail.com | Employment inquiry |
| Evan Pleet | Job applicant | evan.pleet@gmail.com | Employment inquiry |
| Geraldine Ballesteros | Job applicant | geraldineb97@gmail.com | Employment inquiry |
| GWL Realty Advisors | GWL Realty Advisors | Kayla.Cabral@gwlra.com / Carol.Mangente@gwlra.com | Landlord billing (legitimate — NOT spam) |
| Unique VTour | Unique VTour | info@uniquevtour.com | Photography vendor — **LEGITIMATE PARTNER** |
| Maryam Atcha | City Gate Suites | maryam@citygatesuites.com | Payment forwarding — **LEGITIMATE INTERNAL** |

> **Note:** GWL Realty, Unique VTour, and City Gate Suites are operational partners — exclude from do-not-engage list.

---

## 8. Concrete Process Recommendations

### REC 1: Auto-flag "ASAP" or "closing within 14 days" inquiries for same-day quote
**Motivation:** Inquiries with "Stage ASAP" (emails 38782 Sharron Kingston, 40950 amrit brar, 39316 Jeff Thomas) or explicit listing/closing dates consistently convert faster than open-ended timelines. Referrals and realtor-identified leads similarly convert quickly. The one case where Astra sent a quote within hours of a same-day deposit (Tanya Janic, 36938 → 36992) shows urgency = conversion.

**Action:** In the CRM/Zoho intake form, auto-tag any inquiry with "Stage ASAP" or "Stage in 1 Week" as Priority. Assign to Aashika same-day. Set a 4-hour SLA for quote delivery on these.

---

### REC 2: Include photography add-on pricing in every quote upfront — never add post-deposit
**Motivation:** Poonam Mehta (email 40869) complained: "Why did the price go from $2450 to $2982.07?" — the answer was photography + HST added after deposit. This created distrust and required a customer service email to explain. Jared Rogers (email 43493) asked about month 2 and 3 pricing immediately after seeing the quote — he needed to plan.

**Action:** Every staging proposal must include a dedicated line item for photography ($189 or $249 + HST) as an opt-in checkbox, and a renewal pricing table (Month 2 = 50% of staging fee). Add this to the Zoho proposal template. This eliminates the "why is my invoice higher?" CS email.

---

### REC 3: Add a standard "elevator/access pre-flight" section to every proposal sent to condos
**Motivation:** At least 8 scheduling threads in this corpus got stuck on elevator booking requirements (310-109 Front St required 4 back-and-forth emails; 903-16 Concord Pl needed 2+ days notice; 9 Tecumseth required building management to confirm). The 40842 Sophia Bailey complaint ("I was advised the truck will be there between 12-12:30 [but arrived at 1:30]") directly traces to elevator + parking restrictions not captured at booking.

**Action:** In the deposit confirmation email, add a mandatory checklist:
> "For condos and high-rises, please advise: (1) Elevator booking lead time required by building (2) Parking/loading dock restrictions (3) Elevator contact name and phone (4) Whether someone will be on-site or lockbox access"

This moves the friction-gathering upstream, eliminating same-day scrambling.

---

### REC 4: Never leave a quote open more than 7 days without a follow-up — implement automated drip
**Motivation:** On April 2, 2025, Aashika manually sent ~20 follow-up emails in a single batch (37054–37072) to quotes ranging from 3 to 53 days old. Multiple had already gone cold. The Elie Rizk (Ajax) quote sat for 49 days (March 26 → May 14, email 40473) before any follow-up — yet he then committed to payment within hours of the follow-up. Victoria Sklar (Nobleton) waited 27 days, then explicitly chose a competitor (email 38714).

**Action:** Configure Zoho CRM automated follow-up: Day 3 after quote sent → auto-email "Did you have any questions about the proposal?"; Day 7 → "We have availability [nearest 2 dates] — shall we reserve your spot?"; Day 14 → Aashika personal call attempt. Flag any quote >14 days as "at risk" on dashboard.

---

### REC 5: Add a dedicated "staging date + stager" field to all confirmation emails; eliminate the "wrong date" class of errors
**Motivation:** Two confirmed errors in this corpus: (1) Arpit (email 39327) — system sent staging-day prep notification on April 30 when staging was actually May 1; (2) Michael Sistilli (email 39276) — automated destaging email showed April 30 when the agreed date was May 7. Both required reactive correction emails. The Arpit error could have caused crew to load a truck for the wrong day.

**Action:** Before any staging-day or destaging notification fires, add a 24-hour pre-send review step where Aashika or the operations team confirms the date in Zoho matches the agreed date in the email thread. Add the stager's name and cell to all staging-day notifications (currently missing from some — email 40833 had a blank stager field).

---

### REC 6: Require balance payment at deposit stage OR pre-authorize card — end the 3rd/4th reminder pattern
**Motivation:** In this corpus: Chuka (Etobicoke, email 39392) required 4 reminders + "FOURTH REQUEST" language; Antonio Saade (Whitby, email 38772) required 3 reminders; Leanne (Oakville, email 38771) had card declined; Tanya Janic required weeks of follow-up due to financial hardship; Roy WU negotiated a credit for curtains he bought; Brenda New (Niagara) was 19 days overdue at time of email 39250. Each of these required 3–6 staff emails and phone calls.

**Action:** Options: (A) Charge full balance at time of staging (not just deposit) via saved card on Stripe — send invoice 48 hours before staging, auto-charge day-of. (B) For customers who resist, require 50% deposit (not 10–25%). (C) Flag any customer with a prior late-payment history as requiring pre-payment at next booking.

---

### REC 7: Build a standard "lost deal debrief" response — always ask why when deals fall through
**Motivation:** Aashika did this well in several cases — asking Jennifer Bourikas (Hampton St, email 37008), HuiWang (email 37029), Ecko Jay Realty (email 39863) why they declined. The Jennifer feedback was actionable ("current market + existing furniture doesn't mesh with modern staging") and Ecko Jay feedback ("competitor's proposal better fits") provides competitive intelligence. However, many losses in the batch quote follow-up (April 2) received no debrief.

**Action:** Template a single-line debrief question for all explicit declines: "Thank you for letting me know. Just curious — was the price a factor, or was there something else?" Log responses in Zoho under a "Lost Deal Reason" field. Review monthly. This will surface whether Astra is consistently losing on price, style, timing, or competitor relationships.

---

### REC 8: Create a "custom extension" option for the portal (e.g., 2-week, 7-day) to reduce negotiation emails and capture revenue
**Motivation:** Rebecca (Hamilton, email 39399) needed 7 days and offered $100 — not captured. Myles Schwartz (North York, email 44317) requested a 2-week extension — required 3 back-and-forth emails to price and confirm $461.25. Aneri Brahmbhatt requested a complimentary 10-day extension (email 40484) — Astra declined but could have offered a paid short extension instead. The standard portal only offers "extend 30 days" or "schedule pickup" — no middle ground.

**Action:** Add a "Custom Extension" option to the Zoho portal where the customer can select 1 week ($X), 2 weeks ($Y), or 30 days ($Z), with prices auto-calculated at the prorated daily rate. This eliminates the 3-email negotiation loop and captures revenue that is currently being left on the table (Rebecca's $100 was walked away from entirely).