# Anti-AI Writing Style

The mandatory final gate on **every message the cadence agent writes** (emails, LinkedIn, call scripts,
voicemails). Purpose: nothing should read as AI-generated. Complementary to `outbound_voice.md` — that
file says how a rep sounds; this one catches the tells that give a machine away.

> Every copy-producing agent runs its output through this before returning. A message that trips these
> rules is not ready.

---

## 1. Banned phrases (cut or rewrite with specificity)
- "In an increasingly … world" → cut or replace with a concrete fact
- "It's essential / important to note that …" → just say it
- "This represents an opportunity …" → rewrite as a concrete action
- "In the age of AI / digital transformation …" → cut
- "Without a doubt / Undoubtedly …" → cut
- "In conclusion / To summarise …" → never use
- Anything that would fit in a corporate brochure

## 2. Inflated vocabulary (replace with concrete words)
revolutionise, unlock, seamless, leverage, supercharge, game-changer, harness, empower, elevate,
transformative, paradigm shift, holistic, robust, scalable, synergy/synergies, cutting-edge,
next-level, best-in-class, unleash, delve, navigate (metaphorical), tapestry, realm, landscape
(metaphorical), streamline (as filler).

## 3. AI structural patterns (break the rhythm)
- **Metronome rhythm:** AI writes sentences all of medium length. Vary: short, sharp lines with the
  occasional longer one.
- **Mechanical rule-of-three:** not everything in threes. Break the pattern.
- **Antithesis for rhythm — "X, not Y": cut it.** Tightened 2026-09-18 from "vary it", on rep feedback
  (Magnus, AE): after em dashes this is the **second thing he names as the AI tell** — "'this. not that'
  syntax is a pet peeve". Measured on UKI batch 1 the same day: 7 instances across 5 of the 15 drafts.
  The distinction that matters:
  - **Rhetorical antithesis → cut.** "a systems problem, not a talent one" · "in the week, not the month
    after" · "the week it happens, not at month end". The second half adds no information; it exists for
    cadence. Say the first half and stop.
  - **Factual clarification → keep.** "the exchange price, not what your roaster charges you" · "wholesale
    isn't what a supplier charges". Here the contrast *is* the content, and it's doing honest hedging work.
- **No formula line reused across accounts.** UKI batch 1 shipped "Genuine question, not a pitch" as the
  alternate's opener on two different accounts. Each reads fine; as a set it's a template, and a rep
  reading their own briefs in a row sees the seam immediately. Every opener is written for its account.
- **Em dashes and en dashes (— –): ZERO in outbound copy. Not "fewer" — none.** Tightened from
  "overuse" on 2026-08-24, on rep feedback: across batch 3/6 every one of the nine drafted first touches
  opened `Name — ...` and the set carried **24 dashes in 18 pieces of copy**. Each one read fine alone;
  together they were a signature. That is the metronome problem in punctuation form, and a rep reading
  two briefs in a row spots it instantly. Use a comma, a full stop, a colon, or "and". A full stop is
  almost always better — it shortens the line, which the voice file wants anyway.
  **Applies to `first_touch_subject`, `first_touch_body`, `first_touch_alt_subject`,
  `first_touch_alt_body` — every field a prospect can read.** Long-form internal fields
  (`reactivation_*`, `*_rationale`) are exempt: nobody outside Nory reads them.
- **Summary line that restates what was just said** → cut, it's redundant.
- **Lists with a repeated leading gerund** → vary the structure. (And: no bullet lists in a cold email.)

## 4. Voice (human)
- Natural contractions.
- Direct "you" and direct address. Active voice — AI defaults to passive and third person.
- Short. Get to the point in the first two lines. No warm-up ("I hope you're well", "I wanted to reach
  out").
- **But "no warm-up" is not "open on a statistic".** Clarified 2026-09-18 on rep feedback (Magnus, AE),
  who named as his third AI tell "starting emails in what sounds like mid-sentence". This rule was the
  cause: UKI batch 1 read `Hi Michael, AHDB's August report puts UK wholesale butter 43% below...` —
  greeting, comma, straight into a number, with no human reason for the email existing. A person tells
  you **why they are writing to you** before they tell you a fact. The same rep's own best cold email
  does it in two lines and wastes nothing: *"Tom Hatcher, who we know from his time at Mowgli, pointed me
  in your direction. Getting in touch as we work with Sticks n Sushi and are in conversations with the
  other McWin brands to help improve Labour & COGs control."* Reason first, then the fact it sets up.
  Filler is still banned; a reason for writing is not filler.
- If you've made the point, stop. Don't sign off with a summary.
- High signal, zero filler. Specific beats clever.

## 5. Constraints
- Keep standard domain terms as-is (prime cost, GP, COGS, labour %, P&L, multi-site, forecast).
- Respect the outbound register in `outbound_voice.md` — plain human rep, never marketing/ad voice.
- Fix form and tone only; don't change the substance or the offer.
- Never introduce a claim or number that isn't in `knowledge/*`.

## 6. Final test
Read it back (mentally, aloud). Where you stumble, rewrite. If you can't say with certainty whether a
real rep or an AI wrote it, **it's not ready.**
