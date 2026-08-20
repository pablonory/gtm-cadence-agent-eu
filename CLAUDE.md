# GTM Cadence Agent — UKI (Orchestrator)

Multi-agent system that helps **UK & Ireland sales reps run better outbound cadences**. It scores
target accounts on buying signals, learns what actually works from real Gong calls, and produces a
per-account brief + a genuinely personalised first-touch email that the rep drops into a pre-built
Gong cadence template.

> **Fork provenance:** forked 2026-08-20 from `pablonory/gtm-cadence-agent` (the US agent) at
> `05ae6be`, with a first UKI adaptation pass applied. The two repos share architecture, formulas
> and learned rules but diverge on **market config**: signal sources, currency, proof usage, the
> conjunctural register, and the cadence flows. Cross-market learnings should be ported deliberately
> (cite the other repo's commit), never assumed.

**Goal:** same as the US motion — replace ad-hoc "one email + a follow-up" with standardized,
best-in-class multi-channel cadences where only the first touch is bespoke. The agent informs and
drafts; **the rep assembles and activates in Gong.** Nothing sends automatically.
**Owner (UKI):** ⚠️ TO CONFIRM — the UKI equivalent of Lewis (US Head of Sales) for territory +
flows. Do not run real batches until this is named.

---

## Core Rules (apply to every task)

1. **Don't assume. Don't hide confusion. Make tradeoffs explicit.** Missing context or multiple paths → say so, show the alternatives.
2. **Minimal that solves the problem. Nothing speculative.** No abstractions or "for the future" features that weren't asked for.
3. **Touch only what you must. Clean up your own mess.** No collateral changes.
4. **Define success criteria. Loop until verified.** State what "done" means, then check it — no "should work".

---

## Architecture — 3 stages (unchanged from the US agent)

```
ENTRY:  Google Sheet (one row per account, keyed by rep) → group by rep   [UKI sheet TO CREATE]
   │
STAGE 1 — SCORE            per account, every run
   ├─ agents/stage1_signals/  one sub-agent per Tier-1 signal + score aggregator
   └─ writes signal intel + score → HubSpot (the SHARED cadence_brief object — see below)
   │
STAGE 2 — KNOW             built once, refreshed periodically (the shared brain)
   ├─ 2a Positioning:  product · benefits/PMM · pains↔benefits per vertical · JTBD per persona
   └─ 2b Field evidence (Gong):  what works/fails on real calls, per vertical×persona
   │      (scripts/gong_pull.py — same Gong instance as the US; filter to UKI deals/reps)
   │
STAGE 3 — CADENCE
   ├─ OUTPUT A: cadence MAPPING — map each account to the matching Gong flow by exact name
   │            (cadences/UKI_FLOWS.md — ⚠️ the UKI flow set in Gong is NOT yet confirmed).
   │            No agent-designed cadences; no writes to Gong.
   └─ OUTPUT B: per-account brief on the Cadence Brief object (+ optional PDF to Drive):
                snapshot · signal intel · the angle · CUSTOM 1st-touch email · which flow to run.
   │
WEEKLY: digest email per rep — scored accounts + intel gathered.
```

### The one bespoke slot
Only the **first-touch email** is generated per account (Stage 1 signals + Stage 2 knowledge/
evidence, through the anti-AI gate). Every later step is templated by the vertical × persona matrix.

---

## Verticals × Personas — mapped to Gong flows (⚠️ UKI flows unconfirmed)

Inherited working assumption: the same **4 × 4 matrix** as the US (verticals **Coffee & Cafe ·
Fast Casual · FSR · QSR**; personas **C-Suite · Finance · Founder · Operations**; suite from persona:
C-Suite & Founder → **Full Suite**, Finance & Operations → **IM**), flow-name pattern
`<Vertical> × <Persona> (<Suite> · Tier 1)`, plus a **UKI Reactivation** motion (name assumed).
See `cadences/UKI_FLOWS.md` for what must be confirmed before this matrix is trusted — including the
**UKI-specific vertical question: pubs & bars** (a major UK segment the US matrix has no cell for).

## Tier-1 signals (Stage 1)

Same four: New C-suite/ops-finance hire · Funding/investment · Open ops/finance/IT jobs · New
location openings. Research methods in `directives/signals/` are **UKI-first** as of this fork:
premises-licence + planning applications, **Companies House officer appointments + SH01 filings**,
Propel/MCA/Big Hospitality/The Caterer, Caterer.com — with US sources retained, tagged
*(US accounts only)*. All learned mechanics carried over from the US fork's first 80 real accounts
(stage rule, recency-as-discount, ATS probe, anti-fabrication).

---

## MCPs / integrations

| Integration | Via | Used for |
|---|---|---|
| HubSpot | claude.ai connector + the **shared** private app (see below) | Stage 1 write-back; the `cadence_brief` object |
| Google Drive / Sheets | claude.ai connector | UKI entry sheet (⚠️ to create) + per-account PDFs |
| Gong API | local REST (`scripts/gong_pull.py`, Basic auth) | Stage 2b — same Gong instance; pull UKI calls |
| Slack | claude.ai connector | Weekly digest / notifications |
| Apify | local REST (`APIFY_TOKEN` env) | `open_jobs` T2 fallback (`scripts/jobs_probe.py`) |
| Firecrawl | hosted MCP / CLI (`FIRECRAWL_API_KEY` env) | fetch fallback for 403/JS-blocked sources (incl. many council licensing portals) |

**⚠️ The HubSpot app + `cadence_brief` object are SHARED with the US agent and deployed ONCE, from
the US repo.** UKI briefs are rows on the same object, distinguished by owner (UKI reps) + `batch`
labels (`UKI batch N`). Never `hs project upload` from this repo — see `hubspot-app/README.md`.

Secrets: real keys live in a gitignored `.env` / `.mcp.json` (same portal + Gong instance as the US
repo, so the same keys work). The repo only carries `*.example` templates.

---

## Status — forked, NOT yet operational

Blockers before the first UKI batch (tracked in `README.md` → Open questions):
1. **UKI flow owner named** (the Lewis-equivalent) and **UKI Gong flows confirmed** (folder, names,
   reactivation motion) → `cadences/UKI_FLOWS.md`.
2. **UKI accounts sheet created** (`input/README.md` schema) + UKI rep emails validated as HubSpot owners.
3. **UK conjunctural register built** from primary sources (`knowledge/conjunctural/README.md`) —
   the US register was removed at fork; the matcher has nothing to match until UK entries exist.
4. Pubs & bars vertical decision.
Everything else (signal playbooks, scoring, first-touch generator, HubSpot write path, jobs probe)
is inherited working and market-adapted.
