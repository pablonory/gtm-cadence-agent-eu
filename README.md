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

| # | Question | Where it lands |
|---|---|---|
| 1 | **Who owns UKI territory + flows?** (the Lewis-equivalent) | `CLAUDE.md`, `input/README.md` |
| 2 | **Which Gong flows do UKI reps actually use?** Folder, exact names, matrix shape, reactivation motion — Pablo investigating | `cadences/UKI_FLOWS.md` (capture checklist inside) |
| 3 | **Pubs & bars** — a major UK segment with no US-matrix cell; own vertical or fold into FSR? | `cadences/UKI_FLOWS.md`, `context/icp/verticals.md` |
| 4 | **UK conjunctural register** — US entries removed at fork; build UK entries (NLW steps, employer NICs, Tips Act, business rates, commodities) from primary sources | `knowledge/conjunctural/README.md` |
| 5 | **UKI accounts sheet** — create to the `input/README.md` schema; validate rep emails as HubSpot owners | `input/README.md` |
| 6 | Ireland specifics — € proof (Masa is €-native ✓); IE wage/law entries for the register | `knowledge/` |

## Repo layout

| Path | What |
|---|---|
| `agents/` | Sub-agent definitions, grouped by stage |
| `context/` | Product, ICP (verticals + personas), tone of voice |
| `directives/` | Orchestration, signal research playbooks (UKI-first), the learning loop |
| `knowledge/` | Stage 2 knowledge base incl. Gong evidence + the (to-build) UK conjunctural register |
| `cadences/` | Output A — mapping to the Gong **UKI flows** (`UKI_FLOWS.md`, placeholder) + per-cell angle/proof briefs |
| `input/` | The accounts Google Sheet schema (UKI sheet to create) |
| `scripts/` | `gong_pull.py` · `jobs_probe.py` · `conjunctural_match.py` · `reactivation_bundle.py` |
| `hubspot-app/` | ⚠️ **Reference + scripts only — the app/object are deployed ONCE, from the US repo** (shared `cadence_brief` object; see its README) |
| `prototypes/` | Inherited US-era UI prototypes + BUILD_SPEC (historical reference) |
| `output/` | Local staging (gitignored); real deliverables go to HubSpot/Drive |

## Setup

- **Connectors:** HubSpot, Google Drive/Sheets, Slack — authenticate in claude.ai connector settings.
- **Secrets:** copy `.env.example` → `.env` (gitignored). Same Nory HubSpot portal + Gong instance as
  the US repo, so the same `HUBSPOT_PRIVATE_APP_TOKEN`, `GONG_ACCESS_KEY`/`GONG_SECRET`,
  `APIFY_TOKEN`, `FIRECRAWL_API_KEY` work.

Status: **forked, adaptation pass done, NOT yet operational** — see Open questions above.
