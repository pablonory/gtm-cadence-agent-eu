# GTM Cadence Agent — UKI

Helps **UK & Ireland sales reps** run better outbound cadences. Scores target accounts on buying
signals, learns what works from real Gong calls, and hands each rep a per-account brief + a
personalised first-touch email to drop into a pre-built Gong cadence.

> Forked 2026-08-20 from [`pablonory/gtm-cadence-agent`](https://github.com/pablonory/gtm-cadence-agent)
> (the US agent) at `05ae6be`, with a first UKI adaptation pass. Repo named `-eu` as the umbrella;
> **v1 market scope is UKI** (UK + Ireland).

**Orchestration and full design:** see [CLAUDE.md](CLAUDE.md).

## How it works (short version)

1. The UKI territory owner lists accounts per rep in a **Google Sheet** (the entry point — ⚠️ to create).
2. **Stage 1 — Score:** sub-agents research Tier-1 buying signals per account (UKI-first sources) → HubSpot.
3. **Stage 2 — Know:** a knowledge base (product/pains/JTBD) grounded in **Gong evidence** — the £/€
   proof points are UKI-native customer results, quotable directly here.
4. **Stage 3 — Cadence:** the agent maps each account to the matching pre-built **Gong flow**
   (`cadences/UKI_FLOWS.md` — ⚠️ flow set not yet confirmed; briefs mark "flow pending" until it is)
   and writes a per-account brief with a custom first touch.
5. The **rep** assembles and activates the cadence in Gong. Nothing sends automatically.

## Open questions (blockers before the first real batch)

Moved to **`docs/open_questions.md`** — every unknown with an owner and the file its answer unblocks.
The three that gate the first batch: **the UKI owner** (the Lewis-equivalent), **the Gong flow set**
(`cadences/UKI_FLOWS.md`), and **the accounts sheet** (`input/README.md`). The conjunctural register is
✅ built (2026-08-20, 16 UK+IE entries from primary sources).

## Repo layout

| Path | What |
|---|---|
| `.claude/agents/` | The real, dispatchable workers: 4 `s1_*` signal hunters + `ca1_first_touch` |
| `.claude/skills/` | `first-touch` — the one bespoke output |
| `.claude/reference/` | Architecture detail, integration status, the retired-agents ledger |
| `context/` | Product, ICP (verticals + personas), anti-AI writing style |
| `directives/` | Runbooks + signal playbooks (UKI-first), the learning loop |
| `knowledge/` | Stage 2 knowledge base: pains/JTBD/proof (£/€-native), Gong evidence, the **UKI conjunctural register** |
| `cadences/` | `UKI_FLOWS.md` — flow-name placeholder + capture checklist. One file, on purpose. |
| `input/` | The accounts Google Sheet schema (UKI sheet to create) |
| `scripts/` | bundle · digest · Gong pull · jobs probe · conjunctural matcher · state snapshot · firecrawl fetch |
| `lib/` · `tests/` | `gtm_common.py` · stdlib unittest suite (`python3 -m unittest discover tests`) |
| `docs/` | `open_questions.md` (owners) · `reuse_map.md` (fork ledger) |
| `hubspot-app/` | ⚠️ **Reference + scripts only — the app/object are deployed ONCE, from the US repo** (shared `cadence_brief` object; see its README) |
| `output/` | Local staging (gitignored); real deliverables go to HubSpot |

## Setup

- **Connectors:** HubSpot, Google Drive/Sheets, Slack — authenticate in claude.ai connector settings.
- **Secrets:** copy `.env.example` → `.env` (gitignored). Same Nory HubSpot portal + Gong instance as
  the US repo, so the same `HUBSPOT_PRIVATE_APP_TOKEN`, `GONG_ACCESS_KEY`/`GONG_SECRET`,
  `APIFY_TOKEN`, `FIRECRAWL_API_KEY` work.

Status: **forked, hardened (fork-sync of the US `harden-m1` at `cbb37d1`, 2026-09-01), NOT yet
operational** — what gates the first batch is not code: see `docs/open_questions.md`.
