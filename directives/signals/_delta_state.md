# Delta / state layer — how Stage 1 detects *change* (the signal backbone)

> The implementation of the "signals are deltas" principle in `_signal_stack.md`. A buying signal is a
> **change event**, not a static fact — so the agent needs a memory of each account (its state last run)
> to compute what's genuinely **new** this run. Without it, count-based signals can't be detected and
> stale signals get re-flagged forever. Decision set with Pablo, 2026-07-17.

## Two kinds of signal (they use state differently)
| Kind | Signals | How "new" is judged | Needs a stored baseline? |
|---|---|---|---|
| **Intrinsic-date** | funding (announcement date), leadership_hire (start date), new_location (open/announce date) | The event carries its own timestamp — recency is self-evident | No to *detect*; yes to avoid *re-flagging* |
| **Stateful-count** | location count, # open ops/finance roles | No public change-date — only a count comparison reveals the change | **Yes — the baseline is the signal source** |

The stack uses **both**: intrinsic dates judge recency (works on the first run); stored baselines catch
count changes and stop re-flagging.

## State store
- **Location:** one JSON snapshot per account — `output/state/<domain>.json` (**gitignored** — holds real
  prospect data). This is the **detection memory**.
- **HubSpot custom properties = the human-facing outputs** (score, why-now, per-signal present/strength/
  recency, last-run) — reps/Lewis see these; they are NOT the diff store.
- Split rationale: lists (locations, execs, seen postings) are awkward as HubSpot properties and are
  internal diffing detail reps don't need; keep them in the snapshot.

### Snapshot schema (`output/state/<domain>.json`)
```json
{
  "domain": "blankstreet.com",
  "last_run": "2026-07-17",
  "locations": { "count": 9, "sites": ["NYC-SoHo", "NYC-FiDi", "..."] },
  "execs": [ { "name": "...", "role": "COO", "start_date": "2026-06-07", "flagged_run": "2026-07-17" } ],
  "funding": { "round": "Series A", "date": "2026-06-20", "flagged_run": "2026-07-17" },
  "open_roles": [ { "title": "Head of Ops", "location": "NYC", "posted": "2026-07-07" } ],
  "contract_expiry": "2026-10-01"
}
```

## The run cycle (read → observe → diff → score → write)
```
1. READ    output/state/<domain>.json  (prior baseline; empty on first run)
2. OBSERVE current reality per signal (agent WebFetch/WebSearch)
3. DIFF    current − stored → the delta (timestamped) = the signal
4. SCORE   ga_score_aggregator scores the deltas → HubSpot outputs
5. WRITE   ga_score_aggregator writes today's observation back as the new baseline (+ last_run)
```

## Per-signal delta rule
| Signal | Delta = what's new | State field diffed |
|---|---|---|
| **new_location** | sites observed now **not** in `locations.sites` (and count increase) | `locations` |
| **leadership_hire** | an exec present now **not** in `execs` (or start_date <90d and not yet `flagged_run`) | `execs` |
| **open_jobs** | postings not in `open_roles`; also detect roles that **disappeared** (possible hire → pair with leadership) | `open_roles` |
| **funding** | a round newer than `funding.date` | `funding` |
| **contract_expiry** | read from HubSpot; store for reference — not a researched delta | `contract_expiry` |

## First-run rule (no baseline yet)
- Use **intrinsic dates** to flag genuinely-recent items (a hire <90d by its start date, funding <180d,
  opening <180d) even with no baseline.
- **Seed the baseline** from the first observation; start **count-diffing from run 2**.
- Do NOT treat the entire current state as "new" on run 1 (that would flag every existing site/exec).

## Freshness / expiry
- Every stored item carries a date; recency is **recomputed each run** from that date.
- Signals **expire**: a leadership_hire >90d, funding >180d, opening >180d drops out of "present" even
  though it stays in the baseline (so it's remembered, not re-flagged).
- `flagged_run` records when a delta was first surfaced → never re-surface the same item.

## Relationship to the 14-day suppression
The playbooks' 14-day per-signal suppression is a **crude fallback**. True delta detection supersedes it:
once an item is in the baseline with a `flagged_run`, it isn't re-flagged regardless of the window. Keep
the 14-day rule only as a backstop for signals where a baseline isn't available.

## What reads/writes this
- **Signal agents** (`agents/stage1_signals/ga_*`) — READ the snapshot at start, compute their delta.
- **`ga_score_aggregator`** — WRITES the updated snapshot back (current → next baseline) alongside its
  HubSpot outputs.
- No detection code yet — this is the spec the Stage-1 build follows.
