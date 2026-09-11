# UKI Flows — cadence source of truth (two layers, looked up per rep — never built)

> **Status 2026-09-11.** The Gong Engage flow set was captured from the Gong API
> (`scripts/gong_flows.py`, `GET /v2/flows?flowOwnerEmail=<rep>`), not from screenshots. What is
> KNOWN: every flow name, folder, visibility and creation date, per rep. What is NOT knowable from
> Gong: **which flows are live**. Verified 2026-09-11 — the per-flow detail and prospect endpoints
> 404/405, and `/v2/stats/activity/*` returns call activity per user with nothing flow-level. There
> is also no manager shortcut: flow choice is each rep's own, so **only the rep can confirm**
> (`registry/asks/<rep>.txt` is the two-minute Slack question). What we *can* measure is which flows a
> rep has **edited** — Engage edits land in `GET /v2/logs?logType=UserActivityLog` as
> `/ajax/sequences/update-sequence` with the flow id, ~6 months of history. Nobody edits a dead flow,
> so that ranks the survey; it is not proof of sending, and silence is not proof of death. **Never invent a flow name** — and in UKI,
> never *build* one either: a name is looked up, or it is empty.

## How UKI differs from the US — and why the matcher changes shape

The US runs **one shared 16-flow matrix** (`<Vertical> × <Persona> (<Suite> · Tier 1>`), so the US
agent *derives* the flow name from vertical × persona. UKI runs **two layers**:

1. **Company layer** — 73 `Company`-visibility flows every rep sees (`registry/_company.json`). The
   UKI-relevant core is the **"Outbound" folder (40)**: `<Segment> <Persona> - Agentic AI` with
   segments **Bar/Pub · Coffee · Resto** and personas **CEO · Finance · IT · Ops · People**, an
   **SMB** series (`SMB - <Segment|Persona> Agentic AI`), **four reactivation flows by reason** (No
   show · Non-responsive · Product gaps · Timing), MQL/inbound handling and event flows. The folders
   "US Flows"/"USA Flows" (37) are the US agent's matrix, visible here only because the Gong instance
   is shared — **the UKI matcher must never select them for a UKI account.**
2. **Personal layer** — each rep's own flows (`Personal` visibility; team leads create theirs as
   `Shared`). Heterogeneous by design: some reps keep their own vertical × persona sets (Sean's
   "🍻 Pubs - Finance Persona", Louis Grenier's "Finance / Ops / Founder Flow"), some cloned the US
   matrix names into their folder (William, 2026-08-25), many are campaign-, event- or
   account-specific ("Tech Expo 2026", "Boparan Outreach") and are **not templates**.

**Consequence:** `cadence_template` is resolved by **lookup in the rep's registry**, in this order:
the rep's own flow tagged for the account's vertical × persona × motion → the company-layer flow for
the matching segment × persona → **empty** with the note "no matching flow in <rep>'s registry". The
code guard changes from "matches the US name pattern" to "**exists verbatim in this rep's registry**".
(Matcher rewiring is the next build step — `docs/open_questions.md` #11.)

### `live` is tri-state — and an unconfirmed flow may still be SUGGESTED

Waiting for thirteen replies before the first batch would stall the agent on something a rep can
correct in one click. So:

| `live` | Meaning | What the brief does |
|---|---|---|
| `true` | the rep confirmed it | names the flow, `flow_status: confirmed` |
| `null` | not asked / not answered yet | names the flow as a **suggestion**, `flow_status: suggested`, with "from your Gong flows — tell me if it's the wrong one" |
| `false` | the rep said they don't run it | never suggested again |

Suggesting is not inventing: the string comes **verbatim from that rep's own Gong**, so the worst case
is proposing a flow they have abandoned — visible to them in one glance and cheap to correct, against
the certainty of blocking every brief. Corrections arrive through the existing feedback fields
(`rep_feedback_detail`) and are written back to the registry, per `directives/self_improvement.md`.
A flow tagged `event`, `inbound` or `unclassified` is never suggested, at any `live` value.

## Files

| File | What | Committed? |
|---|---|---|
| `uki_reps.json` | The UKI outbound roster (10 AEs + 3 BDRs, confirmed by Pablo 2026-09-11) | yes |
| `registry/_company.json` | The company layer, tagged from names | yes |
| `registry/drafts/<rep>.json` | Per-rep draft registry — personal + shared-with-them flows, proposed tags, `live: null` | yes (Pablo 2026-09-11: flow names may live in the repo) |
| `registry/REVIEW.md` | Master review sheet, all reps — tick live, correct tags. Annotatable in the Obsidian vault | yes |
| `registry/_usage.json` | Flows each rep has **edited** in the last 90 days, from the Gong audit log (`scripts/gong_flow_usage.py`) — the best available proxy for "live" | yes |
| `registry/asks/<rep>.txt` | The exact Slack message for that rep: four questions, question one pre-filled from `_usage.json`. Slack IDs are in `uki_reps.json`; sending is a Slack-connector call, on Pablo's word only | yes |
| `registry/<rep>.json` | **Confirmed** registry — created from the draft once the rep has answered; the only file the matcher reads | not yet — none confirmed |
| `output/gong/flows/<rep>.json` | Raw API pulls | no (gitignored) |

Refresh: re-run `scripts/gong_flows.py` when reps add flows; the diff against the confirmed registry is
the review list. Drafts are regenerated, confirmed files are edited by hand.

## Taxonomy bridge (agent → Gong company layer)

| Agent vertical | Gong segment | Note |
|---|---|---|
| `coffee_cafe` | Coffee | direct |
| `fsr` | Resto | direct |
| `qsr`, `fast_casual` | Resto (or SMB - Restaurant) | Gong has no QSR/Fast Casual split in the company layer — personal layers sometimes do ("QSR Evolution", "QSR: Labour") |
| **`pubs_bars`** (proposed) | **Bar/Pub** | a real UKI segment with 5 company flows + personal ones — resolves the "pubs & bars" question in favour of its own vertical (decision: Pablo) |

| Agent persona | Gong persona | Note |
|---|---|---|
| `csuite`, `founder` | CEO / MD/CEO | Gong does not split founder vs hired exec; keep the agent's split for the angle, map both to CEO for the flow |
| `finance` | Finance | direct |
| `operations` | Ops | direct |
| — | **IT**, **People** | ⚠️ Gong personas the agent does not classify — a gap, not a mapping |

**Suite (IM vs Full Suite)** is not encoded in UKI flow names. It keeps deriving from persona for the
first-touch benefit (Finance/Ops → IM · C-Suite/Founder → Full Suite) unless a registry entry carries
an explicit `suite` tag (US-matrix clones do).

## Reactivation — better than the US here

The company layer has **four** reactivation flows, one per reason the deal died. The reactivation
analysis (`directives/reactivation_deal_analysis.md`) already classifies the reason, so the mapping is
deterministic: `no_show` · `non_responsive` · `product_gaps` · `timing` → the matching company flow.
The single "UKI Reactivation" name previously assumed by `score_accounts.py` / `map_contacts.py`
**does not exist** — retire the assumption when the matcher is rewired.

## Classification rules (market-neutral — in force now)

**Vertical** — Coffee & Cafe (coffee groups, speciality coffee, all-day cafés, bakeries) · Fast Casual
(counter-order, elevated, limited table service) · FSR (full-service, table service; gastropubs here
*until* the `pubs_bars` decision) · QSR (quick-service, high throughput, often franchised).

**Persona** — Founder (founder-led / owner-operator is the buyer) · C-Suite (hired exec at a larger
group) · Finance (FD / Head of Finance / FC) · Operations (Ops Director / Head of Ops / Ops Manager).
The key split is Founder vs C-Suite. Blank persona on the sheet → default from HubSpot title + company
size, and note the assumption in the brief. Contact → persona priority in `map_contacts.py`:
Founder > C-Suite > Finance > Operations; unmatched titles are **unmapped**, never guessed.

## Where the per-cell `cadences/*.md` files went

Removed 2026-09-01 (following the US repo, cbb37d1): the first touch is built from `knowledge/` via
`.claude/skills/first-touch/`; history at `952abff:cadences/`.
