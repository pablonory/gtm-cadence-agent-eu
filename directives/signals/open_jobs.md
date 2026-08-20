# Signal playbook — Open ops / finance / IT jobs

> Versioned research method for the `ga_open_jobs` sub-agent. Adapted from the BDR Clay signal doc
> (Tier 1). The learning loop rewrites this file as detection sharpens.

## What it detects
**Currently open ABOVE-STORE roles** at the target account in **operations, finance, or IT/systems** —
e.g. Ops Manager, Head of Ops, Finance Manager, FC, Systems/IT Manager, Data Analyst, "Head of Restaurant
Systems". Multiple open ops/finance roles at once is a stronger signal than one.

## Why it matters for Nory
Open ops/finance/IT roles signal **operational strain and a systems gap** — they're hiring people to
do work Nory automates (scheduling, inventory, reporting, forecasting). It's a "why now" (they feel
the pain enough to spend headcount) and a talking point ("could a system close some of this gap
faster than a hire?").

## Run the probe first — `scripts/jobs_probe.py` (built 2026-08-12)
```bash
python3 scripts/jobs_probe.py <domain> [--company "Name"] [--json] [--apify]
```
This signal fired only **5/80** in the first two real batches, and the cause was mechanical: careers
pages hand off to an ATS (Paycor · Lever · iCIMS · Workday · ADP · Paylocity · Poached) that WebFetch
can't read, so agents honestly recorded *"unverifiable — not counted rather than fabricated"*. The probe
removes that wall. **Run it before concluding anything about a company's hiring.**

It works in tiers, cheapest and most authoritative first:

| Tier | Method | Cost | Covers |
|---|---|---|---|
| **T1** | The ATS's own **public JSON API**, found by fingerprinting the careers page or by probing candidate tokens | free | Greenhouse · Lever · Ashby · Workable · Recruitee · SmartRecruiters · Personio · Teamtailor |
| **T2** | Apify, scoped to the board URL (`--apify`) | paid | Workday · iCIMS · Paycor · Paylocity · ADP · Poached |

**Why token-probing rather than reading the careers page:** measured 2026-08-12, `insomniacookies.com`
and `portillos.com` both return **403** (Cloudflare) and `sweetgreen.com` renders its board in JS with no
ATS string in the HTML. Asking the ATS APIs directly never touches the company's site, so their bot
protection is irrelevant. On Insomnia Cookies this turned an unreadable board into **1,033 postings**,
correctly surfacing the FP&A Analyst and Director of Procurement — with real post dates.

## Where to look (UKI-first — flipped at fork 2026-08-20)
1. **`scripts/jobs_probe.py`** — the ATS board via its public API. The T1 vendors (Greenhouse, Lever,
   Ashby, Workable, Recruitee, SmartRecruiters, Personio, Teamtailor) are global and cover many UK
   groups unchanged. ⚠️ **Known UKI gap:** UK hospitality leans on **Harri**, Fourth, S4labour and
   Flow — none has a public JSON API in the probe yet. When the probe finds no board, check the
   careers page for a Harri/Fourth fingerprint before concluding; extending the probe for Harri is
   the first UKI L2 candidate (log recall misses to justify it, same trigger discipline as the US).
2. **Company careers page** — worth a look for the ATS link and roles the API misses; often 403.
3. **UK hospitality boards** — **Caterer.com** (the sector default), Otta (London tech-adjacent ops
   roles), Harri's own board pages.
4. **Indeed UK / Google Jobs** — ⚠️ **corroboration only, never the basis of a score.** The
   company-name-search noise problem was measured on the US fork (a "Giordano's" search returned an
   insurance agent, a recycling firm and a different franchisee) and applies identically here.
5. **HubSpot** — any prior notes on hiring/expansion.
6. *(US accounts only)* Culinary Agents, HCareers.

> **LinkedIn Jobs is deliberately not on this list.** Scraping it breaches LinkedIn's ToS and the repo
> rule is explicit (`_signal_stack.md`). It is also redundant: LinkedIn postings are usually mirrors of
> the same ATS the probe reads directly, and LinkedIn adds the same company-disambiguation problem as any
> aggregator. If Nory ever licenses LinkedIn data properly, revisit — until then, don't.

## How to verify
- Confirm roles are **above-store ops/finance/IT** — not FOH/kitchen/marketing.
- Confirm the **employer is the target entity**, not a franchisee or a namesake business.
- Confirm the posting is **live**; `recency_days` = age of the *freshest* relevant posting.
- Count distinct relevant roles → feeds strength. Dedup by title+location (agency reposts inflate counts).

### The corporate vs unit-level line (the thing that makes this signal mean anything)
A crew, barista, line-cook or server req says nothing about a systems gap — every restaurant always has
those open. Equally, a **General Manager, Restaurant Manager, Kitchen Manager, Executive Chef or Shift
Supervisor is in-restaurant however senior it sounds**, and does not count.

But a corporate function word beats an in-restaurant *word*: `IT Security Analyst`,
`Head of Delivery & Digital` and `Manager, Kitchen Systems` are above-store and **do** count.
`scripts/jobs_probe.py` encodes exactly this precedence (`UNIT_TITLE_RE` → `CORPORATE_RE`/`SENIOR_RE` →
`UNIT_WORD_RE`); if you classify by hand, follow the same order.

**Unit-level hiring is not wasted intel.** The probe returns `unit_level_count` and the locations. A full
FOH/BOH slate in a metro they don't yet operate in is a strong pre-opening tell — feed it to
`new_location` as stage/confidence evidence (see that playbook), never to `open_jobs`.

Also remember many ICP accounts **have no corporate function at all** — a 2–5-site owner-operator has
nobody above store level to hire. For them a clean `present:false` with the board actually read is the
correct, informative answer, not a detection failure. Say which board you read.

## Scoring rubric
| Field | Rule |
|---|---|
| `present` | true if ≥1 live **above-store** ops/finance/IT role |
| `strength` (1–5) | 5 = 3+ relevant roles open · 4 = 2 roles · 3 = 1 senior (Director/VP/Head-of) ops/finance role · 2 = 1 non-senior relevant role · 1 = stale/unclear |
| `recency_days` | days since the most recent relevant posting (`null` if the board publishes no dates) |
| `confidence` | **high** = the company's own ATS board read via its API · **med** = careers page or a scraped board · **low** = aggregator only |

## Output
`{present, strength, recency_days, evidence, source_url, confidence, roles: [{title, location, posted}], hook_detail}`
- `hook_detail` = **the first-touch hook material**: the most telling role(s), verbatim from the posting
  (e.g. `"hiring a 'Director of Restaurant Systems' — first systems hire on the careers page"`). A role
  title that implies the systems gap beats a count. Empty if the roles are unremarkable.

## Dedup / suppression
**Primary = baseline diff** (`directives/signals/_delta_state.md`): only postings not in stored
`open_roles` count as new. 14-day suppression is a fallback. Dedup postings by title+location.

## Source & access (v2 — L2 WIRED 2026-08-12)
**`scripts/jobs_probe.py` is the detector.** T1 reads the company's ATS via its public JSON API (free, no
scraper, dated, company-scoped). T2 uses Apify (`APIFY_TOKEN`, gitignored `.env`) only for boards with no
public API, and only scoped to a board URL — it will **refuse** a company-name aggregator search rather
than return noise. See `directives/signals/_signal_stack.md`.

Cost note: T1 is free, so the probe is safe to run on every account every time. T2 costs per run, is
opt-in behind `--apify`, and should be reserved for accounts worth the spend (a real ICP fit on a
Workday/iCIMS/Paycor board).

## Applied feedback
- [2026-08-12] **L2 built and this playbook rewritten around it.** Measured recall was **5/80 (6%)** across
  batch 2 + reactivation batch 1/6, with ATS portals the named cause in 4 accounts and blocked pages in 8
  more. Two things were wrong beyond tooling: (a) the careers page can't be the primary source — Insomnia
  Cookies and Portillo's return 403 and sweetgreen renders in JS; (b) Indeed company-name search, listed
  as source #2, is unusable for scoring (a `"Giordano's"` search surfaced an insurance agent, a recycling
  firm, an HVAC company and a different franchisee). Fix: probe the ATS APIs directly by candidate token.
  Insomnia went from "unverifiable" to **1,033 postings, 2 above-store roles, dated, high confidence**.
- [2026-08-12] **the corporate/unit precedence bug.** The first classifier let any in-restaurant word win,
  which discarded `IT Security Analyst` and `Manager, Kitchen Systems` as unit-level. Corrected so an
  explicit in-restaurant *title* wins but a corporate/senior marker beats an in-restaurant *word*.
- [2026-08-12] **`present:false` is often the right answer, and now a well-evidenced one.** Most ICP
  accounts are small enough to have no above-store function. Reading their board and saying so is a real
  finding; it is no longer indistinguishable from "we couldn't look".
- [2026-08-20] **UKI fork** — probe-first unchanged (ATS APIs are global). Flagged the **Harri/Fourth/
  S4labour gap**: UK hospitality's dominant boards have no public JSON in the probe — extending it is
  the first UKI L2 candidate, gated on measured recall misses (same trigger discipline as the US).
  Caterer.com promoted; Indeed UK is corroboration-only (the aggregator-noise finding carries over).
