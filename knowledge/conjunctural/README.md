# Conjunctural signals — the industry/macro layer (UK & Ireland)

> **Stage 2 knowledge, not Stage 1 detection.** Researched **once centrally and refreshed**, then
> matched to accounts by attributes. One research pass serves every account.

> ⚠️ **Register emptied at fork (2026-08-20).** The US entries (CA wage steps, tip credit, US
> scheduling laws, US commodity series) belong to the US repo and were removed — several concepts
> (tip credit especially) don't even exist in UK employment law. `register/` is empty until UK/IE
> entries are researched **from primary sources**. `scripts/conjunctural_match.py` works unchanged;
> it simply has nothing to match until then, so `first_touch_basis` falls back to `vertical_pain`.

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

## UK/IE candidate entry types (to research — primary sources only, NEVER model memory)

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
`scope.level` = `uk | england | scotland | wales | ni | ireland | council`, since UK employment/rates
law is devolved — a Scotland-only fact must never open an email to a Manchester group.

## Hard rules (unchanged — market-neutral)
1. **Primary, dated sources only.** gov.uk, gov.ie, HMRC, ONS, AHDB, council pages. Never populate
   an entry from model memory — a wrong wage figure destroys credibility faster than sending nothing.
2. **Facts and cost implications only — never advice.** Stating a rate change is fine; suggesting how
   to restructure staffing/tips/contracts around it is legal/tax advice and not ours to give.
3. **No fear-mongering.** State the change and the date.
4. **Politically charged topics are excluded** from cold first touches.
5. **Every entry expires** (`effective_date` + `review_by`); the matcher skips stale entries.

## Entry schema (`register/*.json`) — unchanged
Same shape as the US fork (id, type, title, scope, verticals, personas, status, effective_date,
review_by, direction, fact, quantification{basis,value,how}, source, angle, proof_pairing, caveats).
`quantification.basis` must be a recognized cost/price unit before an entry can be an opener —
a new basis name is a deliberate matcher addition, reviewed, never silent. Commodity entries: vertical
is a coarse proxy — prefer hand-selecting the commodity that matches the account's actual menu.

## Refresh cadence
Commodities monthly · wage schedules quarterly and always before April (UK) / January (IE) steps ·
laws quarterly or on legislative change.
