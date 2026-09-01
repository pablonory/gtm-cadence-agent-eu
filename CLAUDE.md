# GTM Cadence Agent — UKI (Orchestrator)

Helps **UK & Ireland sales reps run better outbound cadences**. For each target account it gathers real
evidence, scores it, and writes a per-account brief plus a genuinely personalised first-touch email into
HubSpot, where the rep reads it and assembles the cadence in Gong. **Nothing sends automatically.**

**Goal:** same motion as the US agent — standardized multi-channel cadences where **only the first touch
is bespoke**. The agent informs and drafts; the rep activates.
**Owner (UKI):** ⚠️ TO CONFIRM — the UKI equivalent of Lewis (US Head of Sales) for territory + flows.
**Do not run real batches until this is named.**

> **Fork provenance:** forked 2026-08-20 from `pablonory/gtm-cadence-agent` (US) at `05ae6be`;
> market-adaptation pass at `952abff`; **fork-sync 2026-09-01** ported the US `harden-m1` pass
> (`cbb37d1`) — real subagents, the delta layer, tests, and the honesty rewrite — with UKI adaptation.
> What carried, what was adapted, what was dropped: `docs/reuse_map.md`. Cross-market learnings port
> deliberately (cite the other repo's commit), never by assumption.

---

## Core Rules (apply to every task)

1. **Don't assume. Don't hide confusion. Make tradeoffs explicit.** Missing context or multiple paths → say so, show the alternatives.
2. **Minimal that solves the problem. Nothing speculative.** No abstractions or "for the future" features that weren't asked for.
3. **Touch only what you must. Clean up your own mess.** No collateral changes.
4. **Define success criteria. Loop until verified.** State what "done" means, then check it — no "should work".

Agents are built to the house doctrine: `~/.claude/skills/agent-doctrine/`.

---

## What actually runs today — and what has never run here

The **infrastructure is live and shared with the US repo** (deployed ONCE, from there): the HubSpot app
(`nory-prod`), the `cadence_brief` custom object (36 properties, two rep-facing cards), and the Python
layer. The US side has 127+ brief records. **UKI has written zero briefs — no UKI batch has ever run.**
Blockers, each with an owner: `docs/open_questions.md`.

The runnable motion (inherited, ported at `cbb37d1`, untested on UKI accounts):

```
domain list (⚠️ UKI sheet TO CREATE — input/README.md)
   │
   ├─ scripts/reactivation_bundle.py     HubSpot deals/contacts/emails + Gong calls/transcripts
   │                                     → output/reactivation/<domain>.json   (gitignored, real PII)
   ├─ scripts/bundle_digest.py           pre-slicer — a worker is never handed a raw bundle >~100 KB
   │
   ├─ STAGE 1 per account:  read baseline output/state/<domain>.json
   │     observe: 4 subagents IN ONE MESSAGE (s1-new-location · s1-leadership-hire · s1-open-jobs · s1-funding)
   │     diff:    scripts/state_snapshot.py      a signal is a CHANGE, not a fact
   │     score:   hubspot-app/scripts/score_accounts.py     pure function
   │     draft:   ca1-first-touch (invokes the first-touch skill) → output/briefs/ (gitignored)
   │     write:   hubspot-app/scripts/upsert_brief.py        the ONLY write path
   │     commit baseline LAST: state_snapshot.py commit      (crash before = cheap re-run)
   │
   └─ conjunctural fallback when score <30 / no signal:
        scripts/conjunctural_match.py --nation <england|scotland|wales|ni|ireland> --vertical <v>
          --persona <p> --locations <n> [--council <c>] --json
```

Sequenced by `directives/full_refresh_runbook.md`; step detail in
`.claude/reference/architecture_notes.md`. Run mode (US decision, inherited): **supervised manual
batches** — no cron, no headless runner. **🚦 A human reads every brief before a rep acts on it.**

### What is NOT built — do not describe these as working
- **Stage-2b Gong evidence packs** — method spec at `directives/stage2b_gong_evidence.md`; nothing runs
  it, and for UKI the pull must additionally filter to UKI deals/reps on the shared instance.
- **Sequence analytics** — Gong Engage is off; the data does not exist.
- **No PDF, no Drive deliverable, no weekly digest, no sheet write-back** (retired in the US 2026-08-24,
  inherited here — see `.claude/reference/retired-agents.md`).
- **Contraction detection** — measured as the most frequent gap (4/10 US accounts were closing sites);
  the stack only detects growth.

---

## The write target — read this before touching HubSpot

**Everything the agent writes lands on the `cadence_brief` custom object — SHARED with the US agent and
deployed ONCE, from the US repo. Never `hs project upload` from this repo** (`hubspot-app/README.md`).
UKI rows are distinguished by owner (UKI reps) + `batch` labels (`UKI batch N`). The agent writes
**NOTHING to COMPANY**: a live Clay pipeline (workspace "Nory Lab", 2,360 companies, same portal) owns
`vertical`, `triggers_score`, `icp_score` and the `*_news_*` family. COMPANY `vertical` is not reusable
as input either — six values disjoint from our four (note: one of them is `Pub`). Classify from the
sheet; treat HubSpot `vertical` as a contradiction check.

Three properties are **rep-owned**, never overwritten by a batch: `rep_feedback`, `rep_feedback_detail`,
`variant_copied`. `status` is shared — never clobber a live `in_cadence`.

---

## Verticals × Personas — ⚠️ the UKI flow set is NOT confirmed

Working assumption inherited from the US 4×4 matrix; **every flow name is pending**
`cadences/UKI_FLOWS.md` (capture checklist inside). Until confirmed: classify vertical × persona
normally (it aims the angle), leave `cadence_template` **EMPTY**, note *"flow pending"*.

- **Verticals:** Coffee & Cafe · Fast Casual · FSR · QSR *(+ the open **pubs & bars** question — a major
  UK segment with no US cell; gastropubs → FSR meanwhile)*
- **Personas:** C-Suite · Finance · Founder · Operations (Founder = founder-led/owner-operator;
  C-Suite = hired exec at scale)
- **Suite from persona:** C-Suite & Founder → **Full Suite** · Finance & Operations → **IM**
- Reactivation motion name **assumed**: `UKI Reactivation`.

**Never invent a flow name.** Known knowledge gaps, flagged in place: Fast Casual has no pain set,
Founder has no JTBD block — borrow and say what you borrowed.

---

## Tier-1 signals — the method is UKI-first, the measurements are US

New C-suite/ops-finance hire (180d) · Funding (365d) · Open ops/finance/IT jobs (current-state) · New
location openings (365d). Method per signal: `directives/signals/` — **UKI-first sources as of the
fork** (premises licences + planning, Companies House, Propel/MCA/Big Hospitality/The Caterer,
Caterer.com; US sources retained tagged *(US accounts only)*). Output shape: `_signal_stack.md`.

**All recall/precision numbers in the playbooks were measured on US batches** (80 accounts + batch 3/6)
— inherited as method evidence, labelled at the point of use; **re-measure on UKI accounts before tuning
anything.** Two US-measured rules that port structurally: run `jobs_probe.py` **before** dispatching the
open-jobs hunter (9 of 10 dispatches were waste), and the UKI ATS landscape (Harri/Fourth/S4labour/Flow)
has no public JSON API in the probe — log recall misses.

**The conjunctural register is UKI-native and live** (16 UK+IE entries from primary sources,
2026-08-20): `knowledge/conjunctural/README.md`. Watch its refresh dates — first expiries Sept 2026.

---

## The workers

| Agent | Does | Feeds |
|---|---|---|
| `s1-new-location` | site expansion: premises licences/planning → openings | `state_snapshot.py` |
| `s1-leadership-hire` | a new above-store ops/finance/C-suite seat (Companies House first) | `state_snapshot.py` |
| `s1-open-jobs` | above-store ops/finance/IT roles, via `jobs_probe.py` | `state_snapshot.py` |
| `s1-funding` | funding / investment / M&A, incl. rigorous negatives (SH01 corroboration) | `state_snapshot.py` |
| `ca1-first-touch` | **the one bespoke output** — primary + softer alternate | `upsert_brief.py` |

The four `s1_*` are genuinely independent — launch all four **in one message**. `ca1-first-touch` runs
after the score exists. **None has a HubSpot tool** — that is how "the write path is deterministic code"
stays structural. `ca1-first-touch` has **no web tools** — a search at composition time only invites an
unverified fact into a rep's email. It invokes the `first-touch` **skill**; naming a skill is not
invoking it.

Real subagents live in **`.claude/agents/`** with YAML frontmatter and are invoked through the Agent
tool — never by reading the file into your own context. A subagent starts with **empty context**: pass
exact file paths, never conversation memory.

**Scale effort to the task.** One account = one worker, 6–15 tool calls (each spec carries its budget).
A batch = at most **5 accounts in flight** (HubSpot rate limits; p90 US bundle was 161 KB). **Never spawn
a subagent for a task under 3 tool calls.** Multi-agent costs ~15× the tokens of a single pass.

**Tool heuristics.** The digest before the raw bundle; `jobs_probe.py` before any web search about
hiring; `conjunctural_match.py` before inventing a why-now; Firecrawl **via
`scripts/firecrawl_fetch.py`** only after a plain fetch 403s or returns empty (the hosted MCP Firecrawl
tools are DEAD — stale key; council licensing portals are a known 403/JS-blocked class where the script
matters). Start broad, then narrow.

---

## Integrations — honest status

| Integration | Via | State |
|---|---|---|
| HubSpot | private-app token in gitignored `.env` | **Wired, shared portal.** The only write path. |
| HubSpot | claude.ai connector | Read works; custom-object read needs re-auth. |
| Gong API | local REST (`scripts/gong_pull.py`) | **Wired, shared instance** — filter to UKI. Calls + transcripts, NOT sequence analytics. |
| Firecrawl | `FIRECRAWL_API_KEY` in `.env`, REST | **Wired via REST only** (`firecrawl_fetch.py`). Hosted MCP tools dead. |
| Apify | `APIFY_TOKEN`, REST | Wired — `jobs_probe.py` T2 behind `--apify`. Known defect: see `mcp_status.md`. |
| Clay | claude.ai connector | Live, owned by someone else. Read-only. |
| Google Drive / Sheets | claude.ai connector | Connected. ⚠️ UKI entry sheet TO CREATE. |
| Slack | claude.ai connector | Connected, unused. |

Secrets: gitignored `.env` (same portal + Gong keys as the US repo). Repo carries `*.example` only.
Detail: `.claude/reference/mcp_status.md`.

---

## Where things live

| Path | What |
|---|---|
| `directives/` | Runbooks + signal playbooks — **the method**, versioned, with Applied feedback |
| `knowledge/` | Pains, JTBD, proof (£/€-native), Gong evidence, **the UKI conjunctural register** |
| `context/` | Product, ICP (verticals/personas/segments), anti-AI writing style |
| `cadences/` | `UKI_FLOWS.md` — the flow-name placeholder + capture checklist. One file, on purpose. |
| `hubspot-app/` | ⚠️ Reference + scripts only — **the app/object deploy from the US repo, never here** |
| `scripts/` | bundle · digest · Gong pull · jobs probe · conjunctural matcher · state snapshot · firecrawl |
| `lib/` | `gtm_common.py` — one `load_dotenv`, one `normalize_domain` |
| `tests/` | stdlib unittest on 3.9 — run `python3 -m unittest discover tests` before trusting a change |
| `.claude/agents/` | The real, dispatchable workers: 4 `s1_*` hunters + `ca1_first_touch` |
| `.claude/skills/` | `first-touch` — the one bespoke output |
| `.claude/reference/` | Orchestration detail kept out of this file (architecture, integrations, retired agents) |
| `docs/` | `open_questions.md` (every unknown, with an owner) · `reuse_map.md` (fork discipline) |
| `output/` | Local staging, gitignored — real prospect PII. Never commit, never upload blindly. |

## Status — 2026-09-01

**Forked, hardened (fork-sync of `cbb37d1`), NOT yet operational.** The conjunctural register is built
(`ea0f161`); the delta layer, workers, tests and write-path guards are ported. What gates the first UKI
batch is not code: the owner, the flows, the sheet, and the pubs & bars call — all in
`docs/open_questions.md` with owners. Until the owner is named, nothing runs on real accounts.
