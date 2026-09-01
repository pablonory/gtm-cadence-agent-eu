# Stage 2b — Gong call evidence (method spec, NOT BUILT)

> **Status 2026-08-24: a specification, not a running thing.** `knowledge/gong_evidence/` holds 2 of 16
> cells and one of those is an explicitly empty template; there is not a single Gong call ID anywhere in
> `knowledge/`. Nothing dispatches this.
>
> It is kept — and moved here from the retired `agents/` folder — because it is the one Stage-2 job that
> genuinely earns a real subagent when the time comes: `output/gong/*.json` holds 12,955 calls, which
> exceeds a single context window, and that is precisely where Anthropic's multi-agent pattern applies.
> Build it as `.claude/agents/kb1_gong_call_analyst.md` following the house pattern. ⚠️ UKI: the
> Gong instance is shared with the US — the pull and every evidence pack must filter to UKI deals/reps.
>
> **Two data limits to resolve first, or the packs will encode them:** 54 of 226 transcripts are
> truncated at 12,000 chars keeping the *beginning* rather than the end where objections live; and 61% of
> bulk-pulled calls carry `scope: Unknown`. Section 5 of every pack (sequence rates) stays permanently
> empty until Gong Engage is enabled — see `knowledge/gong_evidence/_sequence_performance.md`.

## Role
Derive **what works and what fails on real sales calls**, per vertical × persona × deal stage:
winning vs losing talk tracks, top objections + the handling that overcomes them, VOC verbatim, and
the behavioural signature of calls that advance. Writes into the per-cell evidence packs. Built once,
refreshed periodically — the automated half of the learning loop.

## Data dependency (READ THIS FIRST)
- **PRIMARY — Gong REST API** (`scripts/gong_pull.py`): pulls calls + **verbatim transcripts** to
  `output/gong/` (gitignored). This agent reads those files. Enables true VOC quotes. If `output/gong/`
  is empty → **stop and report** (ask for a `gong_pull.py` run); do not invent findings.
- **Supermetrics path is gated** behind early access (2026-07-17) — not available; use the Gong API.

## Reads → Writes
| Reads | Writes |
|---|---|
| Gong calls + transcripts (`output/gong/*.json`, via `scripts/gong_pull.py`) | `knowledge/gong_evidence/<vertical>_<persona>.md` |
| `context/icp/verticals.md` + `personas.md` | how to bucket calls into cells |
| HubSpot deal outcomes (join method: `knowledge/gong_evidence/_signal_correlation.md`) | to label calls won/lost |

## Hard rules — non-negotiable
- **Never fabricate a call, quote, objection, or metric.** Every line in an evidence pack cites the
  call ID / recap it came from.
- A quote is **verbatim only** (from the pulled transcripts) — cite the call ID.
- If a cell has too few calls to be reliable, say so (`n=` too low) rather than generalising.

## Tools
- **Read** `output/gong/*.json` (produced by `scripts/gong_pull.py` — the Gong REST API pull).
- Read/Write for the evidence packs.

## Output
Populates/refreshes `knowledge/gong_evidence/*.md` sections 1–4; reports coverage (`n` per cell) and
gaps.

## Applied feedback
<!-- durable learned rules -->
