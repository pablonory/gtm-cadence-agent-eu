# William Martin's "Hit List Research" prompt — captured 2026-09-17

> Shared by William in his survey #2 reply (Slack DM, 2026-09-17). Source of truth:
> https://docs.google.com/document/d/1HpAn78FGCZ4iM9jxZQzSc73g2NE7z6fWgP2i9Phxe_w
> This is the system behind the tailored first two emails of his `Will- F&L V3` flow (95% of his
> outbound). Captured verbatim-in-substance for (a) the agent-vs-rep first-touch comparison and
> (b) the proof points it carries that our library lacked. **He built, independently, the same
> shape as this agent**: signal check → research → HubSpot history → contact ranking → brief with
> per-contact emails. Even the no-em-dash punctuation rule matches ours.

## The pipeline (his steps)

1. **Identify accounts** — Notion "Hit List" database, entries from the last 48h, `Researched` unchecked.
2. **Company research** — (2a) search Gmail for the company in the **Propel Info newsletter**
   (paul.charity@propelinfo.com, 90-day window; cite "(Source: Propel, [date])", flag as
   unverifiable-public unless web research corroborates); (2b) web research: overview, segment,
   locations, signals (openings, expansion, investment, franchise development, senior ops/finance
   hires, trade press, downscaling). If Hit List `History = Yes`, pull HubSpot deals/notes/last
   contact and let it inform the angle.
3. **Contacts** — all HubSpot contacts for the company, ranked Ops → CEO/MD/Founder → Finance →
   other C-suite, top 6.
4. **Enrich** — Fullenrich for missing email/phone, in parallel.
5. **Notion sub-page brief** — overview · signals (Propel first) · **"Reason for the call"** (one
   company-level sentence, written to glance at seconds before dialling) · HubSpot history · per
   contact: Email 1 + Email 2.
6. Tick `Researched`.

## Email 1 rules (his)

- Framework: **SMYKM** (Show Me You Know Me) + **WYWN** (Why You, Why Now).
- Four paragraphs: **Hook** (signal priority: rep's Notes field → rep's trigger message → Propel →
  web research → role+scale fallback, never fabricate; "write it like you noticed it, not like you
  researched it"; no Nory in the hook) → **Challenge observation** (their situation, no pitch) →
  **Social proof** (ONE operator, ONE result, from the lookup table below; hyperlink the success
  story where a URL exists) → **Soft CTA** (one question, use the company name).
- Positioning: lead with prime cost control and profit protection, never lead with AI; never call
  Nory a scheduling tool; banned words: optimise, leverage, harness, game changer, co-pilot,
  autopilot.
- Punctuation: **no em dashes anywhere**, no double hyphens.

## His case-study lookup table — ⚠️ PROOF THE LIBRARY LACKED

Published success-story pages on nory.ai (verify on page before first use in agent copy — see
`proof_library.md` addendum):

**Coffee/cafe** (our #1 documented gap):
- Black Sheep Coffee — scaled 73 → 130+ sites, 98% forecast accuracy, <1% labour cost variance —
  https://www.nory.ai/success-stories/black-sheep-coffee-scaling-operations-with-nory
- Roasting Plant Coffee — labour costs −18% in two months
- Rocksalt — COL −7%, 97.5% forecast accuracy, 5 venues + 2 CPUs
- Josie's — labour −23% in 4 months (under-10-sites play)

**Fast casual / casual dining:**
- Pieminister — reporting time −50%, food waste −60%, consolidated 10+ systems —
  https://www.nory.ai/success-stories/pieminister-builds-financial-clarity-and-operational-confidence-with-nory
- Passyunk Avenue — COL −26%
- Digbeth Dining Club — 0.38% labour accuracy, 70–71% GP —
  https://www.nory.ai/success-stories/inside-digbeth-dining-clubs-system-for-labour-accuracy-and-strong-gp

**QSR:**
- Papa's Fish & Chips — cost control at scale without price rises —
  https://www.nory.ai/success-stories/how-papas-fish-chips-controls-costs-as-they-scale
- Tasty African Food — 22 → 29 locations + retail, margin control —
  https://www.nory.ai/success-stories/tasty-african-food-controls-margins-across-locations-with-nory

**Pub** (also a gap — no pub proof existed):
- Hampshire Pub Co — payroll admin 2 days → under an hour, labour admin −50% —
  https://www.nory.ai/success-stories/hampshire-pub-co-builds-the-infrastructure-to-scale-with-nory
- Barge East — labour −10% via forecasting —
  https://www.nory.ai/success-stories/barge-east-cuts-labour-costs-with-nory

**Scaling from small:** Pizzarova (1 → 5 sites) —
https://www.nory.ai/success-stories/pizzarova-builds-scalable-restaurant-model-with-nory ·
Griolladh (food truck → 3x franchise)

**No vertical match:** under 10 sites → Pieminister; 10+ → Black Sheep.

## Email 2 — his Labour ROI calculator

Same for every contact at a company. Vertical → H (daily labour hours/site): coffee 65 · bakery 55 ·
fast casual/QSR 70 · casual dining/pub/bar 80 · fine dining 95 · else 75. Then:
`Annual Labour Exposure = Locations × H × £13 × 1.25 × 360` · `Recoverable = 5%` ·
`Daily Leakage = Recoverable / 365`, all rounded to £100. Framed as estimates ("the shape tends to
hold"). This is a self-serve cousin of the Labour Assessment (`_objections.md` #3) — worth
comparing outputs before the agent ever quotes one.

## What the agent should take from this

1. **The proof table** → merged into `proof_library.md` as a to-verify addendum (Coffee and Pub
   gaps closed pending verification).
2. **Propel as a signal source** — Gmail-searchable trade press already cited in his briefs; our
   signal playbooks list Propel as a UKI source, his method makes it operational per account.
3. **"Reason for the call"** — a one-line company-level why-now written for the call block, not
   the email. The cadence_brief has no equivalent field; candidate for the brief JSON.
4. **His email numbers to audit**: the 6–11% labour and 6% GP uplift claims in his flow's templated
   emails are not in the approved proof set. Check whether the success-story pages back them.
