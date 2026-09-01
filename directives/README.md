# Directives

Orchestration logic, research playbooks, and the learning loop.

## signals/ — signal research playbooks
One file per Tier-1 signal. Each is the **versioned research method** for that signal: where to
look, which queries work, how to verify, recency/confidence rules. The matching sub-agent in
each `.claude/agents/s1_*` subagent reads its playbook. These files are what the learning loop rewrites over
time, so each signal-hunter gets sharper.

- `leadership_hire.md`
- `funding.md`
- `open_jobs.md`
- `new_location.md`

## Learning loop (built)
- `self_improvement.md` — how feedback becomes a rule (rewrites signal playbooks + Stage 2 knowledge)
- `feedback_log.md` — running log of rep feedback (good / false positive / stale) + cadence outcomes
- `signals/_signal_stack.md` — the signal-detection architecture (agent-first, augment per recall gap)
- `signals/_delta_state.md` — the delta/state layer (detect *change* vs a stored per-account baseline)

Two feedback sources: (1) reps flagging signals and cadence results; (2) automated — each Stage 2
refresh re-reads Gong and re-derives what converts.
