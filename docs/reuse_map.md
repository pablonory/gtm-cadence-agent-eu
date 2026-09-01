# Reuse map — what this fork carries, adapts, and drops (and from which commit)

> Doctrine rule (`agent-doctrine` §6): cross-repo learnings port **deliberately, citing the source
> repo's commit** — never by assumption. This file is the ledger. US repo:
> `pablonory/gtm-cadence-agent`.

## The two sync events

| Date | Source commit | What |
|---|---|---|
| 2026-08-20 | `05ae6be` | **Fork.** Tracked files only, fresh history; first market-adaptation pass (`952abff`): UKI-first signal sources, £/€, US conjunctural register emptied, US_FLOWS → UKI_FLOWS placeholder with capture checklist. |
| 2026-09-01 | `cbb37d1` | **Fork-sync of harden-m1** — this reboot, guided by the `agent-doctrine` skill + the NotebookLM library ("The Perfect Multi-Agent"). Detail below. |

## Fork-sync 2026-09-01 (`cbb37d1`) — the ledger

### Carried verbatim (market-neutral)
`lib/gtm_common.py` · `scripts/state_snapshot.py` (the delta layer) · `scripts/bundle_digest.py` ·
`scripts/firecrawl_fetch.py` · `tests/` (37 stdlib cases, all pass here on 3.9) ·
`scripts/reactivation_bundle.py` (incl. the **STOP/CAUTION paying-customer guard** — a safety fix) ·
`scripts/gong_pull.py` · `context/anti_ai_writing_style.md` (zero-dash gate) · `.gitignore` additions
(`output/briefs/`, the densest PII) · `directives/signals/_delta_state.md` · `directives/
self_improvement.md` · `directives/reactivation_deal_analysis.md` · `knowledge/` shared files (jtbd,
pains, product, benefits, gong_evidence/*) · `context/` shared files.

### Carried with UKI adaptation
- **`.claude/agents/`** — the five real workers. UKI deltas: source lists mirror the UKI-first playbooks
  (Companies House/CRO as primary corroboration, premises licences + planning, Propel/MCA/Big
  Hospitality/The Caterer, Caterer.com; US sources tagged *(US accounts only)*), £/€ examples,
  UKI_FLOWS/"flow pending" rules, the conjunctural matcher's `--nation` CLI. US-measured evidence kept
  verbatim, labelled with provenance.
- **`.claude/skills/first-touch/`** — one delta: points at `cadences/UKI_FLOWS.md`.
- **`.claude/reference/`** — architecture_notes + mcp_status patched inline (matcher CLI, assumed
  reactivation name, UKI sheet/notebook status); retired-agents rewritten for the UKI ledger.
- **`hubspot-app/scripts/score_accounts.py`** — hardened US version + re-applied UKI naming
  (`UKI Reactivation`, assumed).
- **`directives/signals/leadership_hire.md`** — the Wayback-diff method inserted at #4, framed for UKI
  (complements Companies House: the register dates statutory directors, the page diff catches senior
  hires who never file).
- **`directives/signals/_signal_stack.md`** — the consolidated **output contract** + the batch 3/6
  measurements, with a UKI provenance banner (all ten accounts are US; re-measure here).
- **`directives/stage2b_gong_evidence.md`** — + the UKI filter requirement on the shared Gong instance.
- **`knowledge/proof_library.md`** — Ops-framing inversion carried verbatim; the "pair with a US logo"
  rule **inverted** for UKI (here the local logo IS the UKI one).
- **`DEPLOY_CHECKLIST.md` / `CLAUDE.md` / `README.md`** — the honesty rewrite, restated for UKI facts
  (shared infra live, **zero UKI briefs**, blockers with owners).

### Dropped here, as dropped there (same rationale, verified before deleting)
- `agents/` (17 prose specs — none ever invocable; ledger: `.claude/reference/retired-agents.md`)
- `prototypes/` (BUILD_SPEC.md moved to `hubspot-app/`; the three HTML mockups deleted)
- `cadences/` per-cell files (angle/proof content lives in `knowledge/`; UKI's one divergence from the
  US originals was the UKI_FLOWS reference, preserved in the skill). All in git history at `952abff`.

### NOT carried (US-only, or superseded by UKI work)
- US conjunctural register entries (removed at fork; UKI register built 2026-08-20, `ea0f161`)
- US flow names (`US_FLOWS.md`) and the 127 US brief records (US operational data)
- `feedback_log.md` rows (per-repo log — UKI's starts empty, by design)

## Ported the OTHER way — UKI → US, pending

Logged in this repo's memory + `knowledge/conjunctural/README.md`, citing `ea0f161`:
1. Unrenderable quantifications no longer collect the +5 opener credit (shadowing bug)
2. Recency tie-break on `effective_date` (ties used to resolve by register filename order)
3. The `nations` scope-list pattern for partial-jurisdiction laws (Tips Act/ERA are GB-only)
