# CRM/Gong evidence — signal ↔ closed-won correlation (shared)

> What actually correlates with winning. Feeds the signal weights in
> `hubspot-app/scripts/score_accounts.py`. Join method in this file, below. Source: sales-intelligence app
> (2026-07-17) — HubSpot deals + Gong closed-won/lost corpus + the Nory playbook.

## ⚠️ Confidence: LOW — no clean correlation yet
The corpus lacks enough tagged signal for a statistical correlation table. **Most HubSpot deals have
blank compelling-event (CE) fields** — CRM hygiene, not signal absence. What follows is **directional**
(available deals + the playbook's CE hierarchy), **not validated**. Do not present these as measured
correlations.

## Two different things: prospecting signals vs compelling events
- **Prospecting signals** = researchable public triggers our Stage 1 hunters detect: leadership hire,
  funding, open jobs, new location.
- **Compelling Events (CE)** = what actually drives a deal to close, logged in HubSpot / heard on calls.
  Playbook Tier-1 CEs: **incumbent contract expiry · new site opening · new leadership mandate.**
- Overlap: new site + leadership hire are both. **Contract expiry is a CE only — not externally
  researchable** (it surfaces on the call, not via research). See below.

## Provisional ranking (evidence + playbook)
| Signal / CE | Evidence in Nory data | Playbook | Provisional weight |
|---|---|---|---|
| **New site opening** | appears in HubSpot deal narratives | Tier-1 CE | **high** |
| **Incumbent contract expiry** *(CE, not hunted)* | confirmed live — Insomnia Ltd, Business Case stage | Tier-1 CE (#1) | **high — when known** |
| **New senior hire (COO/CFO)** | present in Heavenly Desserts — a *lost* deal | Tier-1 CE | **medium** |
| **Funding round** | none in provided HubSpot/Gong | not documented | **low — unvalidated** |
| **Open ops/finance jobs** | none (top-of-funnel; won't show in deal data) | — | **keep — top-of-funnel value** |

- **Funding** was Tier-1 in the BDR Clay *outbound* doc but has **zero support in Nory's deal data** →
  down-weight and flag for validation. (May be under-logged, or genuinely weaker for multi-site F&B.)
- **Leadership hire** appears only in a *lost* deal — that's presence, not proven positive correlation.
  Keep, don't over-weight.
- **Open jobs** absence is *expected* (it's a prospecting trigger, not a deal-stage field) — don't
  down-weight it for that.

## Contract expiry — the #1 CE we don't hunt
Strongest closing trigger, but not researchable outbound. So we use it, we just don't hunt it:
- **Stage 1:** if HubSpot has a populated contract-expiry / renewal date, the aggregator treats it as a
  strong **score boost** (not a hunted signal).
- **Stage 3:** every cadence (esp. Finance / Ops) should **probe for the incumbent + contract end date on
  the first call** — a discovery goal, ties to `_objections.md` #2 ("get the contract end date on the
  first call"). Not a first-touch email hook (we don't know it yet).

## The outcome join — method (moved here 2026-08-24)
How a signal↔outcome correlation gets *established*, folded in from the deleted `ga_win_loss_synthesizer.md`
so the method survives the file. The deterministic half already exists in code:
`scripts/reactivation_bundle.py` matches Gong calls to an account by title pre-filter, then **confirms by
participant email domain** — the check that stops a call about pies matching a different pie company.
Extract it to `scripts/gong_match.py` when a second caller needs it; don't re-specify it as an agent.

1. Match Gong calls to HubSpot deals on `opportunity_id`, or on account + timeframe.
2. Segment by vertical × persona.
3. Correlate behaviours / proof points / steps against advance vs stall vs loss.
4. Rank what wins per cell.

**Hard rules.** Needs *both* Gong behaviour and HubSpot outcome — if either is missing, say which and
stop, because a one-sided join is not evidence. State correlation **as correlation, with `n`**; never
present a small sample as a rule. Unmatched calls are reported unmatched, never guessed.

## The gap to fix (RevOps)
Real correlation needs (1) a **required CE field on every closed-won**, populated at close, and (2) a
**structured trigger field at deal creation**. ~2 quarters of clean data → a real correlation table.
Raise with RevOps. Until then, weights above are a **playbook-informed hypothesis**, tuned by the
feedback loop as reps confirm/deny.
