# agents/ — retired 2026-09-01, following the US repo's harden-m1

> The UKI fork carried the same 17 prose "sub-agents" (in `agents/`, grouped by stage) that the US repo
> retired on 2026-08-24 at `cbb37d1`. None was ever invocable — no YAML frontmatter, no `.claude/agents/`
> directory — they were prose a human pasted into context, and the US audit showed they had drifted from
> both the code and the running system. The same findings applied verbatim here (the UKI copies were
> unchanged since fork except naming), so the same decisions were ported on 2026-09-01, citing `cbb37d1`.
> The US repo's `retired-agents.md` carries the full case per file; this records the UKI deltas only.

## What replaced them here

| Was | Now |
|---|---|
| 4 Stage-1 hunters (`ga_funding`, `ga_leadership_hire`, `ga_new_location`, `ga_open_jobs`) | **Real subagents** in `.claude/agents/s1_*.md` — YAML frontmatter, dispatchable, UKI-first sources per `directives/signals/*.md`, and deliberately **no HubSpot tool** |
| `ga_first_touch_email` | `.claude/skills/first-touch/SKILL.md`, invoked by `.claude/agents/ca1_first_touch.md` |
| `ga_score_aggregator` | `hubspot-app/scripts/score_accounts.py` (deterministic; tuning history in its docstring) |
| `ga_cadence_designer` | `hubspot-app/scripts/map_contacts.py` (hard-fails malformed flow names — and in UKI **all** flow names are pending `cadences/UKI_FLOWS.md`) |
| `ga_win_loss_synthesizer` | `knowledge/gong_evidence/_signal_correlation.md` + `scripts/reactivation_bundle.py` |
| 4 Stage-2a builders | maintenance rules at the top of each `knowledge/` file they governed |
| `ga_gong_call_analyst` | **Kept for later** — the one Stage-2 spec that earns a real subagent (`output/gong/` genuinely exceeds one context window). Not built. For UKI it must filter to UKI deals/reps on the shared Gong instance |
| `ga_gong_sequence_analyst` | Retired — Gong Engage is off; the data it specified does not exist (see `mcp_status.md`) |
| `ga_account_pdf`, `ga_linkedin`, `ga_call_script` | Retired for good — the first-touch email is the only bespoke output (US decision 2026-08-24, inherited; expand only on real sales-team feedback) |

## The rule for anything added next

A file in `.claude/reference/` is **documentation**. A real subagent lives in **`.claude/agents/`** with
YAML frontmatter (`name`, `description`, `tools`, `model`) and is invoked through the Agent tool — never
by reading its file into your own context. Before adding one, answer honestly: is the job heavily
parallelizable, does it exceed a single context window, does it interface with many tools? If not, it is
code, a skill, or a paragraph in a playbook. Multi-agent costs roughly 15× the tokens of a single pass
(`~/.claude/skills/agent-doctrine/` — the house law; the escalation ladder comes first).
