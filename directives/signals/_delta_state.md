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
4. SCORE   score_accounts.py scores the deltas → upsert_brief.py writes to cadence_brief
5. WRITE   today's observation is written back as the new baseline (+ last_run)
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
- Signals **expire**: past its window a signal drops out of "present" even though it stays in the
  baseline (so it's remembered, not re-flagged). Windows are **leadership_hire 180d · funding 365d ·
  new_location 365d**, set 2026-08-12 and enforced in `scripts/state_snapshot.py` (`EXPIRY_DAYS`), which
  must keep matching `WINDOWS` in `hubspot-app/scripts/score_accounts.py`. *(This file carried the
  pre-2026-08-12 values 90/180/180 until 2026-08-24.)*
- **First-run windows are deliberately tighter** — 90/180/180 (`FIRST_RUN_DAYS`) — because with no
  baseline a wider window would flag a year of existing history as new.
- `flagged_run` records when a delta was first surfaced → never re-surface the same item.

## The "14-day suppression" — do not cite it
Four deleted agent files cited a **14-day per-signal suppression** as a fallback. That rule **is not
defined anywhere in this repo** — no file states what it suppresses or where it came from. It was
folklore. **Delta detection is the mechanism**: once an item is in the baseline with a `flagged_run` it is
never re-flagged, regardless of any window. If a real suppression rule is ever wanted, define it here
first.

## What reads/writes this — BUILT 2026-08-24
`scripts/state_snapshot.py` implements this spec. Stdlib only, 26 tests in `tests/test_state_snapshot.py`.

| Command | Does |
|---|---|
| `state_snapshot.py read <domain>` | prints the baseline (`{}` on first run) |
| `state_snapshot.py diff <domain> --observation obs.json` | observation → signals, persists nothing |
| `state_snapshot.py commit <domain> --observation obs.json` | same diff, then writes the new baseline |

**The division of labour is deliberate: a signal subagent OBSERVES, this script DIFFS.** Set differences,
date arithmetic and expiry are code, because that is where an LLM quietly gets things wrong. The subagent
supplies only what code cannot infer — `strength`, `stage`, `confidence`, `source_url`, `hook_detail` —
under a `judgement` key, which the script merges into the signal it belongs to. **When the observer and
the diff disagree about `present`, the diff wins** and the disagreement is reported rather than hidden: a
fact already in the baseline is not a new signal.

Two safety properties worth keeping: the write is **atomic** (temp file + `os.replace`), so a crash
cannot corrupt the detection memory; and a **corrupt baseline is fatal, never treated as a first run** —
silently starting over would re-flag the account's whole history as new.

Omitting a key from an observation means "I did not look" and leaves that part of the baseline untouched.
An explicit empty value means "I looked and found nothing". The two are not the same.
