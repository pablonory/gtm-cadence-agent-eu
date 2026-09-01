# Signal playbook — New leadership hire (<180 days)

> Versioned research method for the **leadership_hire** signal. Output shape: `directives/signals/_signal_stack.md`. Adapted from the BDR Clay signal
> doc (Tier 1). The learning loop rewrites this file as detection sharpens.

## What it detects
A new **C-suite, Ops, or Finance leader** who started in-role **within the last 180 days** at the target
account (widened from 90 on 2026-08-12 — see *Applied feedback*). Track ops/finance leaders specifically —
not just CEO/COO/CFO but Head of Ops, Ops Director, Finance Director, Head of Finance, FC, VP Operations.

## Why it matters for Nory
A new ops/finance leader is hired to fix something — usually cost control, consistency, or scale. In
their first months they're auditing tools and open to change (the buying window before the patchwork
calcifies). This is the single strongest "why now" for a prime-cost pitch — the first ~90 days are the
sharpest, which is why the scorer still rewards fresher hires more (×1.0 ≤90d vs ×0.8 ≤180d).

## Promotions and internal moves count
A newly created or newly filled ops/finance seat is the signal — whether the person was hired externally
**or promoted internally**. A long-tenured exec who simply changed title is *not*. When in doubt, ask
whether the *seat* is new to that person; date from when they took the seat.

## Where to look (UKI-first — flipped at fork 2026-08-20)
1. **Companies House officer appointments — check FIRST.** A UK-only advantage the US fork never had:
   **new director appointments are public filings with an appointment date** (free API + web). A new
   ops/finance director at the operating company is a dated, primary-source hire signal. (Not every
   senior hire is a statutory director — treat absence as "not found here", never as "no hire".
   Ireland: CRO submissions, less searchable.)
2. **Press wires + company newsroom** — "appoints", "names <name> as", "welcomes". Search:
   `"<Company>" ("appoints" OR "names" OR "joins as" OR "new") (COO OR CFO OR MD OR "Managing Director" OR "Operations Director" OR "Finance Director")`.
3. **UK trade press people-moves** — **The Caterer** (People), **Propel** (daily people moves),
   Big Hospitality, MCA Insight; The Grocer for bakery/café crossover; Irish trade press for IE.
4. **The company's own leadership page, diffed against the Wayback Machine** — ADDED 2026-08-24 on the
   US fork's batch 3/6 evidence, ported 2026-09-01 (cbb37d1); it belongs near the top there and here. A
   hunter on Backal Hospitality fetched the live team page and the same URL's Wayback capture dated
   2024-11-19: an SVP of Operations & Development present today was **absent** from the older snapshot,
   and the three execs the CRM already knew were shown to be long-tenured. It also caught that
   "Helen Chan" and 2021's "Helen Tran Chan" are one person, not a new hire — a phantom the next run
   would otherwise have reported.

   Why this matters more than it looks: this signal's known weakness is that private-group exec moves
   **never reach trade press and live only on the company site and LinkedIn**, and LinkedIn is walled. A
   leadership page is a *static fact*; a leadership page plus a dated snapshot is a **delta**, which is
   what this whole signal is supposed to be. For UKI it complements Companies House: the register dates
   statutory directors, the page diff catches the senior hires who never file.

   `http://archive.org/wayback/available?url=<url>&timestamp=<YYYYMMDD>` returns the nearest capture.
   Two rules: **the snapshot's date bounds the change, it does not date it** — absent in Nov 2024 and
   present now means "sometime in between", so report `recency_days: null` and set `newly_appointed: true`
   on that exec (see the output contract) rather than inventing a date from the gap. And **do not treat
   page metadata as a date**: a photo filenamed `Screenshot+2026-04-17...` is inference, not a date —
   the hunter that noticed one correctly refused to use it. Keep that restraint.
5. **LinkedIn via WebSearch snippets** — job-change posts are login-walled; snippets are a lead to
   verify, never the sole source (rule unchanged from the US fork).
6. **HubSpot** — is the contact already in CRM with a recent title/company change? (enrichment)
7. *(US accounts only)* NRN People on the Move, Restaurant Business/Dive, metro Business Journals.

## How to verify
- Confirm **role seniority** (ops/finance/C-suite — not a junior or non-relevant function).
- Confirm **start date** → compute `recency_days`. If only month/year is available, use the 1st.
- Cross-check the person is at the **target account** (domain/company match), not a namesake.
- Prefer two sources (LinkedIn + press) before `confidence: high`.
- **A venue-level appointment is not a leadership hire.** Executive chefs, GMs, maître d's and
  restaurant-level managers don't count however well covered they are — the seat must be above-store.

## Scoring rubric
> **Recency is a discount, not a gate** (2026-08-12). Score `strength` on the *seat*, put the age in
> `recency_days`, and let `score_accounts.py` apply the decay (≤90d ×1.0 · ≤180d ×0.8 · beyond 180d not
> counted). Don't down-rate `strength` for age as well — that double-discounts.

| Field | Rule |
|---|---|
| `present` | true if the role is ops/finance/C-suite AND `recency_days ≤ 180` (or undated — see below) |
| `strength` (1–5) | Seniority + relevance, ignore age: 5 = COO/CFO/ops-or-finance head at a multi-site group · 4 = VP/Director of Ops or Finance · 3 = C-suite in an adjacent function (CEO/MD) · 2 = above-store but narrow remit (IT, HR, systems) · 1 = weak/unclear |
| `recency_days` | days since start date — **`null` if no source publishes one** (see below) |
| `confidence` | high = 2 sources + clear date · med = 1 source + clear date, or a confirmed seat with no date · low = inferred |

### Undated but corroborated
If the person is verifiably **in the seat** but no source gives a start date, set `present: true`,
`recency_days: null`, `confidence: med`. The scorer applies ×0.85. This is the common case for private
US groups — Specialty Restaurants' new CFO was confirmed in-seat with an unpublishable start date and was
scored `present:false` under the old rules, which discarded a genuine Finance-persona trigger.
If you cannot establish the seat is new, that *is* `present:false` — don't guess.

### Out of window
A real hire older than 180 days is `present:false` for scoring but still useful context: it often explains
the **persona** even when it can't be the why-now (a hired CFO means C-Suite/Finance, not Founder). Put it
in `note` and use it for classification, as several accounts in the first 80 already did.

## Output (returned to aggregator)
`{present, strength, recency_days, evidence, source_url, confidence, role, person_name, hook_detail}`
- `hook_detail` = **the first-touch hook material**: the single most specific, human-sounding fact a rep
  could open an email with — name + role + one background note, exactly as verifiable from the source
  (e.g. `"Dana Osei joined as Finance Director in June, previously ran finance at a 40-site group"`).
  Never embellish beyond the source; empty if nothing beats the bare fact.

## Dedup / suppression
**Primary = baseline diff** (`directives/signals/_delta_state.md`): an exec already in the stored `execs`
with a `flagged_run` is never re-surfaced. 14-day per-signal suppression is a fallback.

## Source & access (v1)
Agent-first: WebSearch trade press + company announcements (Nation's Restaurant News, Restaurant Business,
MCA). ⚠️ **LinkedIn job-changes are login-walled — agents can't reach them**, so this is the **weakest-recall
signal** of the four. If recall proves poor, the L2 augment is a **compliant people / job-change data API**
(deferred — **not** Apify). **No raw LinkedIn scraping** (ToS/legal). See `directives/signals/_signal_stack.md`.

## Applied feedback
- [2026-08-12] **window widened 90 → 180 days; recency became a discount, not a gate; undated-but-
  confirmed seats now count.** Measured on the first 80 real accounts (batch 2 + reactivation batch 1/6):
  this signal fired **1 time in 80** (only Portillo's). The hires were there — the gate threw them out:
  Bobby Cox's new President (Feb 2026), Cupbop's hired President/COO, Togo's CEO (Sept 2025) and CFO
  (Mar 2025), Insomnia's CFO (Jun 2025), Kapow's exec team (Oct 2025), Specialty Restaurants' CFO
  (in-seat, undated). Under the new model Bobby Cox and Specialty score; the rest remain out of window
  but are retained as persona evidence.
- [2026-08-12] **the venue-level trap is real.** Several accounts surfaced well-covered exec-chef and GM
  appointments that read like leadership news but are restaurant-level. Codified above as an explicit
  exclusion after agents on Ark Restaurants, Jester Concepts and Golden Steer each had to reason it out
  from scratch.
- [2026-08-20] **UKI fork** — Companies House officer appointments promoted to the FIRST check: dated,
  primary-source director appointments are a UK-only advantage (partially offsets the LinkedIn wall).
  Window/decay/undated rules carried over; measured evidence is US-fork data.
