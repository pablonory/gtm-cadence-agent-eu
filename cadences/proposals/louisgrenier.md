# Flow proposal — Louis Grenier

**Status: DRAFT for Pablo's review, then Louis's. Nothing exists in Gong until Louis creates it.**
Built 2026-09-17 from his survey #1 + #2 answers (`registry/louisgrenier.json`) and his book profile
(`output/book_profiles/louisgrenier.json`, pulled 2026-09-16). Copy follows `context/outbound_voice.md`
and passed `context/anti_ai_writing_style.md` (zero em dashes in prospect-facing copy).

---

## The data and the reasons

**His spec (survey #2, 2026-09-16):** 3 flows · flows for ALL contacts · "never mind the vertical
split" · call-heavy, some email, a bit of LinkedIn · short and direct, 6 to 10 days · carte blanche.

**His book (HubSpot):** 221 ICP accounts, 139 SMB (2 to 9 sites) + 69 MM (10 to 29). Contacts on his
ICP accounts by persona: Operations 227 · Founder 176 · C-Suite 111 · Finance 93.

**Why three persona flows and how they cover "all contacts":**

| Flow | Personas covered | Contacts in his book | Suite (from `personas.md`) |
|---|---|---|---|
| A · Owners & C-Suite | Founder + C-Suite | 287 (176+111) | Full Suite |
| B · Operations | Operations | 227 | IM |
| C · Finance | Finance | 93 | IM |

- Founder and C-Suite merge into one flow: same decision altitude, same suite, and the C-suite JTBD
  rule says this persona gets the FEWEST touches ("an owner or MD will not read five emails") — so
  flow A is the shortest of the three.
- Vertical is handled where it can be handled honestly: the **bespoke first touch** (step 1, written by
  the agent per account) carries the vertical-matched pain and proof. The templated steps use only
  **vertical-neutral proof** (forecast accuracy within 1 to 2% of actuals; the UK 10-location ~£50k/yr
  benchmark; 10 to 20% labour reductions "customers typically see") — per `proof_library.md`'s rule of
  never quoting a QSR win to a coffee prospect, which a vertical-agnostic flow cannot guarantee.
- Multi-threading: `map_contacts.py` classifies every contact on the account; on an MM account all
  three flows can run at once on different people. That is what "flows for all contacts" means in
  practice.

**Honesty notes (also for Louis):**
- Founder has **no JTBD block** in the knowledge layer (documented gap, do-not-improvise rule). Flow A
  uses the C-Suite frame plus the phone script's owner language. When the Founder JTBD gets built from
  real calls, flow A's copy gets a revision.
- **No reply/open/meeting rates exist per flow** (Gong doesn't expose them). Structure choices below
  come from `segments.md` (SMB wants compressed), the C-suite fewest-touches rule, and Phil's proven
  3-line skeleton + phone script (`outbound_voice.md`). We measure by rep feedback on briefs, not by
  invented benchmarks.
- Every number in the copy traces to `proof_library.md` / the positioning proof set. No exceptions.

**Proposed Gong names** (Louis can rename; the registry stores whatever he creates, verbatim):
`LG · Owners & C-Suite` · `LG · Operations` · `LG · Finance`

---

## Flow A — LG · Owners & C-Suite (Full Suite) · 6 days, 3 calls, 2.5 emails, 1 LinkedIn

Covers Founders (owner-operators, mostly his SMB accounts) and hired execs (his MM accounts). Shortest
flow: this persona doesn't read long sequences. Goal of every touch: book 20 minutes and get off.

**Day 1 · Email 1 — THE BESPOKE SLOT.** Written by the agent per account (signal-led, vertical-matched
proof, sources linked in the brief). Louis never writes this one; the brief hands it to him.

**Day 1 · Call 1** (same day as the email, afternoon):
> "Hi {first}, this is a sales call. Do you mind if I take 30 seconds to say what we do, then you tell
> me if it's worth a chat?"
> [yes] "We're a centralised system for the back office. We put the top three lines of your P&L into a
> live report, per site. Is that worth a conversation?"
> [book it, get off the phone]

**Day 2 · LinkedIn connect** — no message, no pitch. Just the connect.

**Day 3 · Call 2 + voicemail** (under 20 seconds, spoken):
> "Hi {first}, Louis at Nory. I emailed you Monday about {the signal / margin per site}. One thing
> worth 20 minutes: how groups your size hold margin while adding sites. I'll try you once more
> Thursday."

**Day 5 · Email 2** (templated):
> **Subject:** margin at ten sites
>
> Hi {first}, one great site runs on instinct. Holding the same margin across ten is a systems
> problem, and most groups find that out a year late. We give multi site groups one live view of
> labour and COGS per site, so the discipline scales with the estate. Customers typically see 10 to
> 20% off labour cost. Worth 20 minutes on how comparable groups add sites without the margin
> slipping?

**Day 6 · Call 3, then the close email** (two lines, only if the call doesn't connect):
> **Subject:** last one from me
>
> Hi {first}, I'll stop here. If margin per site becomes the priority this quarter, the 20 minutes
> stands. Good luck with the new sites either way.

Objection notes for the calls (from `_objections.md`): "not the right time" → ask what would have to
be true for it to be the right time, book a dated callback. Franchise or group structure → "are you
the right person, or does this sit at group level?"

---

## Flow B — LG · Operations (IM) · 8 days, 4 calls, 3 emails, 1 LinkedIn

His biggest contact group (227). Frame: hours back + every site running the same way. The ask is the
Ops parallel of the Labour Assessment: rebuild one site's week off the forecast, before any commitment.

**Day 1 · Email 1 — THE BESPOKE SLOT** (agent-written per account).

**Day 1 · Call 1** (pattern interrupt, then the Ops one-liner):
> "We help your GMs make better decisions across your two biggest cost lines while they're running
> the restaurant. Is that worth a conversation?"

**Day 2 · Call 2** (other end of the day than call 1; no voicemail yet).

**Day 3 · LinkedIn connect** — no pitch.

**Day 4 · Email 2** (templated):
> **Subject:** rotas and orders off one forecast
>
> Hi {first}, most ops leads I speak to are still building rotas by hand and guessing orders, then
> losing hours to both. It's not profit leading work. Our forecast runs within 1 to 2% of actuals,
> and the rota and the order both come off it. Here's a low effort way to test it: we rebuild one
> site's next week, rota and order, off the forecast instead of by hand. No commitment, you just
> compare. Want me to set that up?

**Day 6 · Call 3 + voicemail:**
> "Hi {first}, Louis at Nory. I emailed about rebuilding one site's week off a forecast instead of by
> hand, just to compare. Takes nothing from your side. I'll try you again Monday."

**Day 8 · Call 4, then the close email** (if no connect):
> **Subject:** one site, one week
>
> Hi {first}, last one from me. The offer stands: one site, one week, rota and order rebuilt off the
> forecast so you can compare it against the by-hand version. If the admin hours ever get old, you
> know where I am.

Objection note: "GM rotas need judgment" → "your GM still makes the call, they just make it with
actual sales forecast data instead of gut feel."

---

## Flow C — LG · Finance (IM) · 9 days, 3 calls, 3 emails, 1 LinkedIn

Smallest group (93) but proof-led and the clearest ask in the playbook: the Labour Assessment.
Finance wants a £ number tied to their P&L, not a story.

**Day 1 · Email 1 — THE BESPOKE SLOT** (agent-written per account).

**Day 1 · Call 1** (pattern interrupt, then):
> "We put labour and COGS live per site, so the month end stops being a surprise. Is that worth a
> conversation?"

**Day 3 · Email 2** (templated):
> **Subject:** the labour % you find out about too late
>
> Hi {first}, every finance lead I speak to has a version of the same problem: labour and GP drift
> shows up at month end, four weeks after it happened. Nory shows labour % and COGS live, per site. A
> 10 location group typically recovers around £50k a year. If you'd rather have a number for your own
> P&L than a benchmark, we run a Labour Assessment: your labour % and your site count, a modelled £
> figure, before any commercials. Worth doing?

**Day 4 · Call 2 + voicemail:**
> "Hi {first}, Louis at Nory. I emailed about the Labour Assessment: your labour % and site count, a
> modelled £ figure, nothing to buy first. I'll try you once more this week."

**Day 6 · LinkedIn connect + one line** (after connect accepted):
> "Sent you a note on the Labour Assessment. One number, your P&L, no commercials. Happy to share an
> example output."

**Day 8 · Call 3.**

**Day 9 · Close email:**
> **Subject:** the offer stands
>
> Hi {first}, I'll leave it here. The Labour Assessment stands: your sites, your labour %, a modelled
> £ figure, no commercials attached. If the month end surprise gets old, it takes one reply.

Objection note: unclear ROI → this whole flow IS the counter. Never say "it'll save you time" to
finance; the £ figure modelled on their cost base is the format they respond to (real output shape:
"labour savings of £40k, GP variance saving of £11k").

---

## What happens after Louis approves

1. Louis edits anything he wants (voice, timings, asks) and creates the three flows in Gong. The agent
   never writes to Gong.
2. He replies with the exact names as created. They go into `registry/louisgrenier.json` as
   `live: true` with persona tags, and the matcher names them on his briefs.
3. His 15 to 20 account sheet runs as the first batch: per account the agent writes the bespoke first
   touch (step 1) and the brief says which of the three flows fits which contact, via the contact map.
4. After the first batch: his `rep_feedback` on the briefs is the measurement. No invented reply-rate
   claims, Gong doesn't expose them.
