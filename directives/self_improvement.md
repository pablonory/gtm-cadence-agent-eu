# Self-Improvement Layer — how the agent gets sharper

The system is **not static**. Every time a rep or Lewis says "this signal was wrong / this email
landed / this account was a waste", that judgment becomes a durable rule applied at the right place.
No feedback is lost, nothing stays only in chat.

> Adapted from the paid-media repo's `self_improvement.md` for the cadence agent.

---

## Three feedback sources

1. **Human** — a rep flags a signal (false positive / stale / spot-on) or a cadence result (email got a
   reply / bounced / "this angle was off"); Lewis flags territory or targeting. **Includes the rep UI
   thumbs**: the 👍/👎 on each brief (`rep_feedback` on the Cadence Brief / PDF response) is captured
   feedback — a run-start step reads new verdicts since last run and classifies them like any other
   feedback. **A 👎 opens a free-text box** (`rep_feedback_detail`, built 2026-08-13 — supersedes the
   earlier plan of a fixed signal/angle/copy multiple-choice) so the rep says in their own words what was
   off; a run-start step reads new detail text the same way it reads a signal miss report and classifies
   it (wrong signal, wrong persona/contact, stale hook, tone, live-thread collision, factually wrong…).
   Free text over multiple-choice because the real reasons in the first ~114 accounts didn't fit three
   buckets — e.g. "right signal, wrong contact" or "correct but they're mid-conversation with someone
   else" aren't cleanly signal/angle/copy.
2. **Automated** — every **Stage 2 refresh re-reads Gong** and re-derives what converts, so the
   knowledge base and cadence copy improve without anyone typing feedback.
3. **Measured** — the signal scorecard (below): per-signal precision/recall proxies + outcome joins.
   Humans say what *felt* wrong; the scorecard says what *is* underperforming. Both feed the same
   Apply step.

---

## The measured loop — the signal scorecard

"Get better and better at identifying signals" requires numbers, not vibes. Three cheap measurements,
accumulated per signal type in `output/state/_metrics.json` (gitignored, same store as the baselines):

| Metric | Proxy | Captured when |
|---|---|---|
| **Precision** | of signals surfaced to reps: % verdicted true vs false/stale (rep thumbs + explicit flags) | each rep verdict |
| **Recall (miss log)** | every signal a rep/Lewis found manually that the agent missed — logged with signal type + the source that had it | whenever a miss is reported |
| **Outcome join** | reply/meeting rate of first touches, split by which signal types were present + which signal the hook used (Gong sequence data × HubSpot) | each Stage 2 refresh |

**Scorecard duties:**
- `ga_score_aggregator` appends per-run counts (signals found per type, confidence mix) to `_metrics.json`.
- The **weekly digest** includes one scorecard line per signal type: found / confirmed / false / missed.
- **Every Stage 2 refresh reviews the scorecard** and proposes (never silently applies) weight or
  playbook changes.

**Acting on it (the pre-committed triggers from `_signal_stack.md`, now concrete):**
- A signal's **precision < ~60%** over 20+ verdicts → tighten its playbook verify rules first, then
  down-weight in the aggregator if still failing.
- A signal's **misses cluster on one source** → add that source to the playbook's "Where to look".
- **`leadership_hire` recall stays poor** (the known-weak signal) → that's the trigger to buy the
  compliant people/job-change API (L2). `open_jobs` recall weak → wire the Apify actor.
- **Outcome join shows a signal type doesn't correlate with replies/meetings** → down-weight it no
  matter how good its precision is (funding is already the cautionary example).
- Any weight change lands in `ga_score_aggregator.md` → "## Applied feedback", dated, with the metric
  that justified it. The formula stays stable; only weights move.

---

## The 3 levels of optimization

### 1. PROCEDURAL (orchestrator — `CLAUDE.md`)
How the pipeline flows: stage order, gates, hand-offs, when to trigger what, dedup/suppression rules.
- Trigger: "always skip X", "don't push a PDF without a score", "re-run signals every 14 days not 7".
- Applies in: `CLAUDE.md` pipeline flow.

### 2. AGENTIC (a sub-agent in `agents/`)
A specific agent's behaviour: what it emphasises, avoids, how it researches, its output shape.
- Trigger: "the funding agent keeps flagging old rounds", "first-touch emails are too long".
- Applies in: that `agents/**/ga_*.md` file → **"## Applied feedback"** section at the end.

### 3. SIGNAL-PLAYBOOK (`directives/signals/`)
A specific signal's research method: where to look, which queries work, recency/confidence rules.
- Trigger: "leadership-hire keeps missing LinkedIn 'started a new role' posts", "location signal
  should trust Companies House over press".
- Applies in: that `directives/signals/<signal>.md` file → **"## Applied feedback"** section.
- **This is the file the learning loop rewrites most** — each signal-hunter gets sharper over time.

---

## Operating procedure

**Capture** — inline (rep/Lewis comments during a run) or explicit (a direct "record this: …" note, or a
`/feedback` command if one is set up for this repo).

**Classify** every piece of feedback:
- **Type**: `correction` (wrong) / `confirmation` (right, keep) / `preference` (taste).
- **Level**: procedural / agentic / signal-playbook.
- **Target**: exact file.
- **Duration**: one-off or durable.

**Apply**:
1. If durable → write the rule in the target file's **"## Applied feedback"** section, actionable and
   concise. Procedural → update `CLAUDE.md`.
2. ALWAYS append to `directives/feedback_log.md` (most-recent first): date, level, target, type,
   feedback, action.
3. Save as a **project memory** of type `feedback` (with **Why** + **How to apply**) so it survives
   across sessions.
4. Confirm to the user what changed and where.

**Consult** — the orchestrator reads `feedback_log.md` + `feedback` memories at the start of a run;
every agent checks its own "## Applied feedback" before producing output.

---

## "## Applied feedback" — standard format
```markdown
## Applied feedback
- [YYYY-MM-DD] [correction/confirmation/preference] — [actionable rule]. (source: user feedback)
```

## Critical rules
- **No feedback stays in chat.** Rule on file + log + memory, always.
- **One rule, one place.** Never duplicate across levels.
- **Actionable, not vague.** "Better emails" is not a rule. "First touch ≤ 90 words, one ask" is.
- **Reversible.** If the user changes their mind, remove/update the rule and log the change.
- **Always confirm** what changed and where.
