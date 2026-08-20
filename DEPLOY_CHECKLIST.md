# Deployment checklist — US-era reference (UKI deltas at top)

> **UKI fork (2026-08-20):** this checklist documents the US v1 deploy and is kept as reference.
> The UKI deltas are shorter because the heavy lifting is already deployed:
> - **No HubSpot deploy** — app + `cadence_brief` object are live and shared (see `hubspot-app/README.md`).
> - **To create:** the UKI accounts sheet (`input/README.md`) · a `UKI Cadence Agent/` Drive folder ·
>   a "UKI cadence targets" saved view (filter on owner/batch).
> - **To confirm:** the UKI flow set in Gong (`cadences/UKI_FLOWS.md`) · the UKI territory owner ·
>   UKI rep emails as HubSpot owners.
> - **To build:** the UK conjunctural register (`knowledge/conjunctural/README.md`).


**Reviewed 2026-07-17.** What must be true before/at deploy, and the honest spec-vs-runnable picture.

## ⚠️ What this repo IS (read first)
This is a **specification + prompt + knowledge layer**, not executable code. The "agents" are markdown
role definitions; the knowledge/cadences are content. Nothing runs on its own yet. There are two ways
to operate it:
- **(A) Session-driven (v1 recommended):** run it inside a Claude session that has the connectors
  authenticated — Claude follows `CLAUDE.md` + the agent specs, does the research/scoring/drafting live.
  Good for low volume (Lewis's US AEs).
- **(B) Orchestrated (later):** build a runner (Claude Agent SDK / scripts in `scripts/`) that executes
  the pipeline headless. Not built yet.

So "deploy" for v1 = complete the setup below, then run mode (A) on a first real account.

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
- [ ] **HubSpot properties — ALIGN, don't duplicate.** HubSpot already carries Clay-era signal/enrichment
      props: `vertical`, `triggers_score`, `icp_score`, `expansion_news_*`/`financial_news_*`/
      `franchising_news_* [enrichment][signals]`, `website_intent_signal`, `nory_value_prompt`. **Decide:**
      reuse these (map funding→financial_news, new_location→expansion_news, reuse `vertical`) vs write to a
      clean `nory_agent_*` namespace — depends on whether the Clay enrichment pipeline still owns them.
      Only create the genuinely-missing (why-now, persona, leadership_hire, open_jobs, per-account score).
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
