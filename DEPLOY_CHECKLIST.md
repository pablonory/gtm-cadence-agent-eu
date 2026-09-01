# Deployment checklist — US-era reference (UKI deltas at top)

> **UKI fork (2026-08-20):** this checklist documents the US v1 deploy and is kept as reference.
> The UKI deltas are shorter because the heavy lifting is already deployed:
> - **No HubSpot deploy** — app + `cadence_brief` object are live and shared (see `hubspot-app/README.md`).
> - **To create:** the UKI accounts sheet (`input/README.md`) · a `UKI Cadence Agent/` Drive folder ·
>   a "UKI cadence targets" saved view (filter on owner/batch).
> - **To confirm:** the UKI flow set in Gong (`cadences/UKI_FLOWS.md`) · the UKI territory owner ·
>   UKI rep emails as HubSpot owners.
> - ~~To build: the UK conjunctural register~~ ✅ built 2026-08-20 (`knowledge/conjunctural/README.md`).


**Reviewed 2026-07-17.** What must be true before/at deploy, and the honest spec-vs-runnable picture.

## ⚠️ What this repo IS (read first — rewritten 2026-09-01, following the US repo's cbb37d1)
**No longer spec-only.** The shared infrastructure is in production: a deployed HubSpot app (`nory-prod`),
a live `cadence_brief` custom object with 36 properties, two rep-facing cards, and the Python layer
(delta snapshots, scoring, digesting, the single write path) — all deployed ONCE from the US repo and
shared. The US side has 127+ brief records written; **UKI has written none yet** (blockers in
`docs/open_questions.md`). The dispatchable workers live in `.claude/agents/`; the retired prose specs
are documented in `.claude/reference/retired-agents.md`.

**Run mode (US decision 2026-08-24, inherited): supervised manual batches** in a Claude Code session with
the connectors authenticated. No cron, no headless runner — checkpoints exist to resume after a failure,
not to run unattended.

## Pre-deploy setup
### Connectors — verified 2026-07-17
- [x] **HubSpot** — connected (pablo@nory.ai, acct 139694830), **READ works**.
- [x] ✅ **HubSpot WRITE enabled (2026-07-17)** — reconnected with write scope: **COMPANY write = AVAILABLE**
      (+ NOTE), `manage_crm_objects` usable → Stage-1 company-property write-back unblocked. (CONTACT/DEAL/CALL
      write still need re-auth, but v1 only reads those.)
- [x] **Google Drive/Sheets** — connected (read/search work).
- [x] **Slack** — connected (digest channel TBD — not needed for v1).
- [x] **Supermetrics** — connected.
- [ ] ⚠️ **Gong via REST API (primary Stage 2b)** — Supermetrics Gong is **gated behind early access**, so
      go direct: set `GONG_ACCESS_KEY`/`GONG_SECRET` in gitignored env, run `scripts/gong_pull.py --transcripts`
      (built). Until pulled, Stage 2b stays template-only.
- [x] **HubSpot properties — DECIDED (US repo 2026-08-24, applies portal-wide).** Every agent-written
      field lives on the `cadence_brief` custom object, which already carries `score`, `why_now`,
      `persona`, `vertical`, `signals_json`. No new COMPANY property, no `nory_agent_*` namespace.
      **Why:** the Clay pipeline is **live** — workspace "Nory Lab" is connected and 2,360 companies
      carry `triggers_score` (same shared portal, so this collision risk is identical for UKI). It owns
      `vertical`, `triggers_score`, `icp_score` and the `*_news_* [enrichment][signals]` family.
      Also: COMPANY `vertical` is **not reusable** — its six values (`QSR/Fast Casual`, `Bakery`,
      `Coffeeshop`, `Pub`, `Fine Dining`, `Other`) are disjoint from the agent's four. Read it as a
      contradiction check against the sheet, never as the source. (Note for the pubs & bars question:
      the portal enum has a `Pub` value — evidence the segment exists in CRM even though the agent
      matrix has no cell.)
- [ ] **Accounts Google Sheet** — does NOT exist yet; create to `input/README.md` schema.
- [x] **Google Drive folder** `US Cadence Agent/` — **CREATED 2026-07-17** (id `1f0d-62p2kSSXPis8Bb8owAV1Dg-zkUvt`).
      Per-rep `<rep-email>/` subfolders + `_weekly/` created later (need real rep emails from the sheet).
- [ ] **Accounts Google Sheet created** to the schema in `input/README.md` (Rep/Company/Domain/Vertical/
      Persona/Locations + agent-written columns) and shared with the agent. Link recorded in `input/`.
- [ ] **Google Drive folder** `US Cadence Agent/<rep-email>/` per rep (rep sees only their own).
- [ ] **Secrets in gitignored env** (never committed): `APIFY_TOKEN` (Stage-1 jobs augment, optional);
      `GONG_ACCESS_KEY`/`GONG_SECRET` (**primary Stage-2b source** — for `scripts/gong_pull.py`).
- [x] **Cadences already built by Lewis in Gong** — the **US Flows** folder (16 cells + USA Reactivation).
      The agent maps each account to the matching flow by exact name (`cadences/UKI_FLOWS.md`); no agent
      cadence hand-off. *(Follow-up: expand `cadences/*.md` angle/proof briefs to Fast Casual + Founder.)*

## Runnable vs spec-only (set expectations)
| Piece | State |
|---|---|
| Stage 1 signal detection + delta/state | **Spec** — agents describe read→diff→write; runs live in mode (A). No standalone code. |
| Stage 1 → HubSpot write-back | Runnable in mode (A) once properties exist. |
| Stage 2a positioning (`knowledge/*`) | **Built + seeded.** |
| Stage 2b Gong evidence | **Blocked on data** — needs Gong creds + `gong_pull.py` run (Supermetrics gated). `gong_pull.py` built; templates + shared `_*.md` in place. |
| Stage 3 cadence cells (9) | **Built** (drafts for review + Gong build). |
| Stage 3 Output B (per-account PDF) | **Spec** — `ga_account_pdf`; PDF build/Drive upload not coded (`scripts/build_pdf.py` planned). |
| Weekly digest | **Spec** — not built. |
| Apify jobs augment | **Documented, not wired.** |

## Open decisions (non-blocking)
- Signal-scoring 0–100 scale: define once, keep stable (aggregator).
- Leadership-hire recall: accept trade-press-only for v1, or add a people-data API.
- Multi-concept groups: separate motion or ignored for v1.

## Data-quality dependencies (see `REVOPS_DATA_GAPS.md`)
Real metrics (reply/meeting rates, signal correlation, persona conversion) need RevOps logging fixes —
until then, cadence rhythm + signal weights are **playbook hypotheses**, tuned by the feedback loop.

## Recommended first move
**Dry-run mode (A) on one real account end-to-end:** sheet row → Stage 1 signals + delta snapshot →
score → HubSpot → first-touch draft → PDF draft to Drive. Fix what breaks, then widen to a rep's list.
