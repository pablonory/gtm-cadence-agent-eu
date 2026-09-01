# Segments — location bands (scoring + routing)

> Segment thresholds used by Stage 1 scoring and by routing. Location count comes from the sheet
> (`Locations`) or HubSpot enrichment. Bands adapted from the BDR team's Clay signal doc routing
> logic (see memory `nory-clay-signal-doc`) and Nory's acquisition target (multi-location, 2+ sites,
> core = mid-market, goal = enterprise).

## Bands (authoritative — set by Pablo/Lewis, 2026-07-17)

| Band | Locations | Segment weight | Routing |
|---|---|---|---|
| **Enterprise / strategic** | 30+ | highest | AE owner or BDR acts on any signal |
| **Mid-market (core)** | 10–29 | high | BDR acts |
| **SMB** | 2–9 | medium | act on hot-account / strong signal; else lighter touch |
| **Out of focus** | 1 (single-site independent) | — | excluded — not an acquisition target |

## Rules
- **In focus = 2+ locations.** Single-site independents are out of scope (per Nory's acquisition target).
- **Segment weight × signal weight = score contribution** (see `hubspot-app/scripts/score_accounts.py`). A funding
  signal at a 20-site group outweighs the same signal at a 3-site group.
- **Core today = mid-market;** strategic goal = enterprise expansion. When two accounts tie on score,
  prefer the higher band.
- Location count also shapes the **cadence intensity** — larger groups justify the full multi-channel
  cadence; emerging accounts can use a lighter touch (decision with Lewis if we split cadence length
  by band).

> These bands are the *account* segmentation. The *messaging* segmentation is Vertical × Persona
> (`verticals.md` × `personas.md`).

## Band history (resolved 2026-07-17)
Earlier sources disagreed — Clay doc (2–8/8–15/15+), sales-intel app (1–5/6–20/20+), business plan
(2–5/5–30/30+, which Phil called "skewed — ignore"). **Authoritative bands above (2–9 / 10–29 / 30+)
supersede all of these.** Note: the observed-cycle table below was bucketed by the *app's* old bands
(1–5 / 6–20), which only roughly map to the official ones — read it as directional, not exact.

## Observed US sales cycle by segment (directional)
> HubSpot `days_to_close` on US closed-won + Pilot deals (sales-intel app, 2026-07-17). **Small sample
> (~22 deals), inbound-skewed, a few complex deals move the average.** These are *deal-close* cycles
> (create→close) — many are inbound owner-operators closing same-day — **NOT** outbound-cadence
> durations. Use to calibrate cadence *intensity/length by band* and set rep expectations, not to set
> cadence length literally.

| Band (app) | Observed cycle | Notes |
|---|---|---|
| SMB (1–5) | **~12–15 days** (range 0–29; same-day owner-operator inbound common) | solo decision-maker = fast |
| MM (6–20) | **~18–22 days** closed-won; **45–55 days** for Pilot/implementation | consultant/CFO involvement adds 15–25 days |
| ENT (20+) | no closed-won in snapshot | — |

**Cadence implication:**
- **SMB:** owner-operators move fast once interested → keep the cadence **short and punchy**, push for a
  quick yes; a full 19-day / 14-touch flow may over-run a solo decision-maker. Consider a compressed SMB cadence.
- **MM:** longer cycle + more stakeholders (Finance / consultant) → the **full multi-threaded cadence** fits.
- Faster cohort = inbound owner-operators (0–8 days); **Finance/CFO involvement lengthens it** (matches
  Q7: Finance is the later-stage seat).
