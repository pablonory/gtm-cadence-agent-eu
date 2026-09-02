# Conjunctural signals — the industry/macro layer (UK & Ireland)

> **Stage 2 knowledge, not Stage 1 detection.** Researched **once centrally and refreshed**, then
> matched to accounts by attributes. One research pass serves every account.

> ✅ **UK/IE register built 2026-08-20** (same day the US entries were removed at fork) — 16 entries
> in `register/`, all researched from live-fetched primary sources with a verbatim supporting quote
> per entry: UK wages (NLW/NMW April 2026 steps, LPC April 2027 projection), employer NICs, GB tips
> law, England business rates 2026, Employment Rights Act 2025 timeline, the temporary children's-
> meals VAT window, commodities (butter, coffee — beef/energy/eggs checked and excluded as
> immaterial), and Ireland (NMW, PRSI + Oct 2026 step, tips act, pension auto-enrolment). Nearest
> expiries: `vat_childrens_meals_2026` (2026-09-01), commodities (2026-09-20), `ie_employer_prsi_
> 2026_rates` (2026-09-30) — and re-verify wage/rates entries after the Autumn Budget / Budget 2027.
>
> **Matcher adapted 2026-08-20** — the fork note originally claimed `conjunctural_match.py` "works
> unchanged", which was wrong: its scope logic only understood `federal|state|city`, so UK-level
> entries would never have matched. It now speaks UKI geography (`--nation`/`--council`, scope
> levels below) and renders £/€ from a required `quantification.currency` (`GBP`|`EUR`) — a money
> basis without a currency is not usable as an opener, same fail-safe as the basis whitelist.
> `"uk"` never matches an Ireland account; an account with no known nation matches nothing.
> Three further matcher changes made while building the register, each worth porting to the US repo:
> an unrenderable quantification no longer collects the +5 usable-opener credit (it could shadow a
> genuinely usable entry into the vertical-pain fallback), ties break toward the fresher
> `effective_date` (a just-landed step beats a year-old standing rate), and a `nations` scope level
> (`scope.nations: ["england","wales","scotland"]`) exists for GB-only extents — the Tips Act 2023
> and ERA 2025 do NOT extend to NI, which plain `"uk"` would have got wrong.

## Why this exists
Measured on the US fork's first 80 real accounts, **44% produced zero Tier-1 signals** and fell back
to the generic vertical-pain angle. Conjunctural signals fill that gap with something **true right
now, in their jurisdiction, with a date attached**:

```
vertical pain      always true, generic          ← today's fallback
conjunctural       true NOW, their nation/council area, dated  ← this layer
account signal     specific to them              ← Stage 1, always wins when present
```

## The rule that makes this work (read before writing copy)
"Labour costs are rising" is the most clichéd opener in hospitality. A conjunctural email only beats
the fallback if the macro fact is **quantified against that account's own footprint and tied to a
date**:

- ❌ "With rising labour costs across the industry…"
- ✅ "The NLW steps again in April — across your 8 sites' rota that's the number you'll be
  re-modelling in Q1."

The unit is **macro event × account attributes** (nation · vertical · site count · service model),
never macro news on its own. If it can't be quantified on their footprint, fall back to the vertical
pain.

## UK/IE entry types (researched 2026-08-20 — refresh from primary sources only, NEVER model memory)

| Type | What to capture | Primary source |
|---|---|---|
| `minimum_wage` | **National Living Wage / NMW April steps** (UK) · **National Minimum Wage** (IE, January steps) | gov.uk LPC/BEIS pages · gov.ie / WRC |
| `employer_costs` | **Employer NICs** rate/threshold changes (the big 2025 shock has follow-ons) · IE employer PRSI | gov.uk HMRC · Revenue.ie |
| `tips_law` | **Employment (Allocation of Tips) Act 2023** — in force, allocation + records duties · IE Payment of Wages (Tips & Gratuities) Act 2022 | gov.uk · gov.ie |
| `business_rates` | Business-rates revaluations / hospitality relief changes (England; Scotland/Wales differ — scope carefully) | gov.uk VOA · devolved equivalents |
| `scheduling_law` | UK has no US-style predictive-scheduling laws — check zero-hours/guaranteed-hours legislation status before creating entries | gov.uk / parliament bills |
| `commodity` | Butter/beef/coffee/energy input costs | ONS producer prices · AHDB series · Ofgem |
| `vat` | Any hospitality VAT rate change (a perennial UK lobby topic — only if actually scheduled) | HMRC |

Every entry: same JSON schema as before (below), same `review_by` expiry discipline. **Scope field:**
`scope.level` = `uk | england | scotland | wales | ni | ireland | council | nations`, since UK
employment/rates law is devolved — a Scotland-only fact must never open an email to a Manchester
group. `nations` carries an explicit `scope.nations` list for extents that are neither one nation
nor the whole UK (e.g. `["england","wales","scotland"]` for GB-only employment law like the Tips
Act 2023 and ERA 2025, which do not extend to NI).

## Hard rules (unchanged — market-neutral)
1. **Primary, dated sources only.** gov.uk, gov.ie, HMRC, ONS, AHDB, council pages. Never populate
   an entry from model memory — a wrong wage figure destroys credibility faster than sending nothing.
2. **Facts and cost implications only — never advice.** Stating a rate change is fine; suggesting how
   to restructure staffing/tips/contracts around it is legal/tax advice and not ours to give.
3. **No fear-mongering.** State the change and the date.
4. **Politically charged topics are excluded** from cold first touches.
5. **Every entry expires** (`effective_date` + `review_by`); the matcher skips stale entries.

## Entry schema (`register/*.json`)
Same shape as the US fork (id, type, title, scope, verticals, personas, status, effective_date,
review_by, direction, fact, quantification{basis,value,**currency**,how}, source, angle,
proof_pairing, caveats) — with one UKI addition: `quantification.currency` (`GBP`|`EUR`) is
**required** on any money basis (`per_hourly_employee_per_year`, `per_site_per_year`); without it
the matcher refuses to use the entry as an opener.
`quantification.basis` must be a recognized cost/price unit before an entry can be an opener —
a new basis name is a deliberate matcher addition, reviewed, never silent. Commodity entries: vertical
is a coarse proxy — prefer hand-selecting the commodity that matches the account's actual menu.

## The rep-facing surface — the UKI Market Signals page

The register's working UI for reps (built 2026-09-02): an interactive page that mirrors
`conjunctural_match.py` client-side — account fit (nation × vertical × persona × sites, plus an
optional rep-owned staff/site estimate for the estate-level line), area filters (Workforce ·
Inventory & COGS · Tax & site economics, derived from `type`), the dated-events timeline, and six
sector-context cards from `market_context.json` (context only, never openers). Expired entries retire
themselves client-side via `review_by`.

- **Regenerate** after any register/context change: `python3 scripts/render_market_artifact.py`
  → `output/reports/uki_market_signals.html` (gitignored). Template:
  `knowledge/conjunctural/artifact_template.html`.
- **Deploy for reps:** copy the rendered file to the `pablonory/uki-market-signals` deploy repo as
  `index.html`, commit, push — Netlify redeploys on push (connect/manage in the Netlify WEB UI only;
  the CLI is logged into the wrong account, area rule).
- **Market library:** NotebookLM notebook "UKI Market Signals"
  (`ad7a916a-ef84-4e79-a55c-d74c5880136a`, pablo@nory.ai — check `nlm login --check` before every
  upload). Holds the curated market sources + this register rendered to markdown + the signal
  playbooks (repo is source of truth). `market_context.json` cards are extracted from it, each
  verified against the cited verbatim text.

## Refresh cadence
Commodities monthly · wage schedules quarterly and always before April (UK) / January (IE) steps ·
laws quarterly or on legislative change.
