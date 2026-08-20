# Signal playbook — New location openings

> Versioned research method for the `ga_new_location` sub-agent. Adapted from the BDR Clay signal doc
> (Tier 1). The learning loop rewrites this file as detection sharpens.

## What it detects
The target account **adding sites** — at any stage from *permit filed* through to *recently opened* —
within the last 12 months, or a stated expansion plan ("opening 10 sites in 2026").

## Why it matters for Nory
New openings are exactly when prime cost drifts: new teams to schedule, new inventory to control, no
baseline forecast, and finance sees the leak only at month-end. The more sites added per quarter, the
worse the blind spot. Strongest when paired with funding or a new ops/finance leader. Location count
also drives the segment band (`context/icp/segments.md`).

## Earlier beats bigger — the stage rule (added 2026-08-12)
**A site that hasn't opened yet is a better signal than one that has.** Before opening, the operator is
still choosing systems and the rep is early; three months after opening, the systems are bedded in, every
competitor has congratulated them, and the angle is stale. So this playbook scores by **stage**, and
pre-opening stages score *higher* — the reverse of the pre-2026-08-12 rubric, which rewarded already-open
sites and rated "announced/planned" a mere 2.

Set `stage` on the signal to one of:

| `stage` | Meaning | Typical lead time |
|---|---|---|
| `permit_filed` | Liquor-licence application, building permit, or health-dept new-establishment filing | 3–12 months before opening |
| `announced` | Named site + location publicly confirmed, not yet open | 1–9 months |
| `fit_out` | Under construction / "coming soon" page / hiring an opening crew | weeks–months |
| `opened` | Trading | already live |

Permits and licences are the **first required check**, not a fallback — they are public, dated, and land
months ahead of press. In the first 80 accounts agents kept finding them unprompted (a Chelsea Market
liquor licence + community-board filing, a groundbreaking six days old, a health-inspection record for an
*unannounced* third site) while the press-led signals they scored were routinely 60–130 days stale.

## Where to look (UKI-first — flipped at fork 2026-08-20; permits-first rule carried over)
1. **UK premises licences & planning — check these FIRST.** The UK analogue of the US permits rule,
   and just as early: **premises licence applications** (Licensing Act 2003 — each council publishes a
   licensing register/current-applications list), **planning applications** (council planning portals;
   change-of-use to restaurant/café is a months-early tell), and in Ireland **fire safety / commercial
   planning applications** (local authority portals). Search:
   `"<Company>" ("premises licence" OR "licensing application" OR "planning application") "<town>"`,
   plus the council's licensing + planning registers directly. A filing names the address and carries a
   date — exactly what press coverage of small groups lacks. ⚠️ Council portals are fragmented and
   frequently JS-heavy or fetch-hostile — use Firecrawl when WebFetch fails (see `_signal_stack.md`).
2. **Company site / social** — store-locator **diff vs stored state** (the backbone), "now open",
   "coming soon" pages, Instagram/LinkedIn "we're opening in <city>" posts.
   ⚠️ Treat the company's *own* post promoting an existing site as **marketing, not an opening date** —
   one account in the US fork's first 80 promoted its fifth site ~8 months after it opened.
3. **UK/IE trade + local press** — **Propel** (the daily openings/deals wire), MCA Insight,
   Big Hospitality, The Caterer, Restaurant Online; Hot Dinners (London), The Manc/Confidentials
   (regional), Eater London; Irish Times / Irish Independent food pages, LovinDublin.
4. **Companies House** — new incorporations / registered-address changes as corroboration.
5. **Google Maps** — a new listing corroborates an opening (not primary; listings lag and misattribute).
6. **HubSpot** — known location count to compute the delta.
7. *(US accounts only)* state ABC liquor licences, city permit portals, What Now <City>, Eater <city>, NRN.

## How to verify
- Confirm the site belongs to the **target group** (brand match, not a franchise of a different owner
  unless that's the target). In the first 80 accounts two agents caught "new location" stories that
  actually belonged to a *different franchisee* of the same brand — always check whose site it is.
- Identify the **stage** (`permit_filed` / `announced` / `fit_out` / `opened`) and say which.
- Capture **how many** and **where** → count feeds strength; total count feeds the segment band.
- `recency_days` = days since **the dated event you are scoring** (the filing date for `permit_filed`,
  the announcement for `announced`, the opening for `opened`).
- **A reopening, rebrand, or concept swap at an existing address is not a new site.** Nor is a
  temporarily-closed or fire-damaged site. Nor is a closure — never spin contraction as expansion.

## Scoring rubric
> **Recency is a discount, not a gate** (2026-08-12). Score `strength` from **stage + scale**, put the age
> in `recency_days`, and let `score_accounts.py` apply the decay (≤90d ×1.0 · ≤180d ×0.8 · ≤270d ×0.6 ·
> ≤365d ×0.4 · beyond 365d not counted). Don't also down-rate `strength` for age.

| Field | Rule |
|---|---|
| `present` | true if a site addition at any stage within **365 days** |
| `strength` (1–5) | Stage + scale, ignore age: **5** = 3+ sites in flight, or an aggressive named plan, or a permit/licence filed for an unopened site · **4** = 1–2 sites `announced` or in `fit_out` · **3** = 1–2 sites `opened` · **2** = vague plan with no named site, or a single small/concession site · **1** = unconfirmed rumour |
| `stage` | `permit_filed` \| `announced` \| `fit_out` \| `opened` — **required** |
| `recency_days` | days since the dated event — `null` if genuinely undated (scorer applies ×0.85) |
| `confidence` | high = permit/licence filing, or company locator + a second source · med = one credible source · low = social or maps listing only, or an undated own-channel post |

**One expansion, scored once.** If you find both a permit and the opening it led to, they are the *same*
event at two stages — score the **more actionable** one (the earlier stage) and mention the other in
`evidence`. Do not count both. Different sites, of course, both count toward `new_sites_count`.

## Output
`{present, strength, stage, recency_days, evidence, source_url, confidence, new_sites_count, total_locations, locations: [...], hook_detail}`
- `hook_detail` = **the first-touch hook material**: the specific, checkable fact a rep could open with —
  place names + timing, as the source states it (e.g. `"opened Charlotte and Raleigh this quarter, third
  and fourth NC sites"`). Never vaguer than the source; empty if nothing beats the bare count.
  For a pre-opening stage, the hook is the *timing pressure*, not congratulation — e.g.
  `"licence filed for the 15th St site, so a new kitchen is being costed from scratch right now"`.

## Dedup / suppression
**Primary = baseline diff** (`directives/signals/_delta_state.md`): only sites not in stored
`locations.sites` count as new. 14-day suppression is a fallback. Don't recount a prior-run site.

## Source & access (v1)
Agent-first: WebFetch the company store-locator and **diff vs the stored location count/list** (delta
detection — the backbone), plus trade press. Persisting prior state is what makes this reliable. Apify
could scrape awkward locators if agent fetch falls short, but it's not needed by default. See
`directives/signals/_signal_stack.md`.

## Applied feedback
- [2026-08-12] **permits promoted to the first check; strength rubric inverted to favour pre-opening;
  `stage` field added; window widened to 365 days with recency as a discount.** Measured on the first 80
  real accounts (batch 2 + reactivation batch 1/6): this signal was **88% of every detection we made**
  (45/80 accounts; `funding` 0/80, `leadership_hire` 1/80, `open_jobs` 5/80), so in practice the score was
  "quality of the location signal × segment size". Two problems showed up in the detail: the hits were
  mostly **already-open** sites 60–130 days old, and the old rubric actively *penalised* the earlier,
  more actionable stages (`announced/planned` scored 2 while an opened site scored 4). Agents were also
  finding permits, liquor licences, groundbreakings and health-department filings **unprompted** and
  discarding them as unscoreable. This revision makes the earliest dated stage the strongest signal.
- [2026-08-12] **unit-level hiring is a corroborator, not its own signal.** "Hiring a full FOH/BOH slate in
  a new metro" reliably precedes an opening (seen on Union Joints' El Roy's, The Salty Donut, Amo Sami's).
  It does **not** qualify for `open_jobs` (which is corporate-only, by design) — use it to raise
  `confidence` or `stage` on this signal instead, and say so in `evidence`.
- [2026-08-20] **UKI fork** — sources flipped UKI-first: premises-licence + planning applications
  replace US permits as the first check (same earlier-beats-bigger logic; council portals are
  fetch-hostile → Firecrawl fallback). Stage rule, 365d window, recency-discount and the marketing-post
  trap all carried over unchanged; the measured evidence behind them is US-fork data.
