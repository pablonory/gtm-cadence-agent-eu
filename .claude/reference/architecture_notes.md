# Architecture notes — the reactivation run, step by step

> **UKI fork provenance:** ported 2026-09-01 from the US repo's `.claude/reference/architecture_notes.md`
> at `cbb37d1`. Every measured number in this file (bundle counts, truncation rates, recall tables,
> Portillo's/Backal worked examples) was measured on the **US corpus** — inherited as method evidence,
> re-measure on UKI batches before tuning anything against it. UKI deltas are patched inline: the
> conjunctural matcher speaks `--nation`, and the reactivation flow name is **assumed, unconfirmed**
> (`cadences/UKI_FLOWS.md`).

Offloaded from `CLAUDE.md` to keep the always-loaded file small. This is the detail for the one motion
that actually runs. Sequenced by `directives/full_refresh_runbook.md`; the reasoning per account is in
`directives/reactivation_deal_analysis.md` — read that in full before writing anything, it is the
authority on what may and may not be claimed.

## Step 0 — before the batch

- Confirm the account: `claude auth status --text` must say `pablo@nory.ai`. This repo processes real
  HubSpot and Gong data.
- Read `directives/feedback_log.md`. Rules learned from reps live there and in each playbook's
  `## Applied feedback`.
- `python3 hubspot-app/schema/create_schema.py --check` — confirm the live object matches the schema
  file before writing anything into it.

## Step 1 — gather (deterministic, read-only)

```
python3 scripts/reactivation_bundle.py <domain> --company "<Company>"
```

Writes `output/reactivation/<domain>.json`. What it does, and the parts worth knowing:

- Finds the company by `domain`, then walks associations for deals, contacts and logged emails.
- Filters to **dead** deals: stage id in the pipeline's closed-lost set, or `hs_is_closed_lost`, or a
  reason-label regex. It discovers reason properties dynamically — custom pipelines vary the name, and
  four different variants appear across the corpus (`closed_lost_reason`, `closed_lost_reason_new`,
  `nurture_reason`, and a long custom goals field).
- **Collapses same-day "- Clone" duplicates** into one lost cycle, tagging the rest `_duplicate_of`.
  **87 of 109 bundles carry this warning** — it is the most frequent judgement call in the motion, and
  the one most likely to silently report two dead deals where there was one.
- Matches Gong calls by title pre-filter, then **confirms by participant email domain**. That second
  check is what stops a call about pies matching a different pie company. It is also strict: 36 of 109
  accounts confirmed zero calls, and on 11 accounts it dropped every candidate (one at 395 → 0).

**Known limits, both real:**
- **24% of transcripts (54 of 226) are truncated at 12,000 chars**, and `flatten_transcript` keeps the
  *beginning*. For closed-lost analysis that is backwards — the objection and the real reason live at the
  end of a call. A 99-minute discovery survives as roughly its first 13 minutes.
- 61% of bulk-pulled calls carry `scope: Unknown`, the likely cause of the confirmation misses above.

The bundle's `warnings[]` array is the best thing in the file. **Every warning is signal** — address it,
never drop it. Note that agent-authored prose (`_duplicate_note`, `warnings`) sits alongside CRM facts
with only an underscore prefix to distinguish it.

## Step 2 — analyse (judgement)

Follow `directives/reactivation_deal_analysis.md` start to finish. Set
`reactivation_evidence_basis` **first** — it determines what may be claimed. Then the four narratives and
the structured `reactivation_json`.

Where the account has no signal of its own (`score < 30` or nothing present):

```
python3 scripts/conjunctural_match.py --nation <england|scotland|wales|ni|ireland> --vertical <v> --persona <p> --locations <n> [--council <council>] --json
```

Only usable when it returns a quantification — an unquantified macro cliché is worse than the generic
vertical-pain fallback. Never launder a conjunctural fact as an account-specific signal.

## Step 3 — score (deterministic)

```
python3 hubspot-app/scripts/score_accounts.py <accounts.json>
```

Pure function, no HubSpot calls, prints JSON. The formula and its full tuning history are in that file's
docstring — that is the log, not a markdown file. `motion: "reactivation"` maps to `UKI Reactivation`
instead of a matrix cell — an ASSUMED name until `cadences/UKI_FLOWS.md` is confirmed ("flow pending").

## Step 4 — write (the only write path)

```
python3 hubspot-app/scripts/upsert_brief.py <brief.json>
python3 hubspot-app/scripts/map_contacts.py <domain> [--dry-run]
```

`upsert_brief.py` resolves the owner from the rep email, upserts on `domain`, and associates company and
contact. **Do not PATCH HubSpot directly instead** — every guard lives in this script, and bypassing it
is how stale fields and wrong associations happen.

`map_contacts.py` classifies every CRM contact on the company into a persona (priority
**Founder > C-Suite > Finance > Operations**, so "Founder & CEO" → Founder and CFO → C-Suite), groups
them under the matching flow, and writes `contacts_json` plus associations. Titles matching no persona
are listed **unmapped**, never guessed.

## Step 5 — the rep reads it

Two cards on the `cadence_brief` record: the Cadence Agent tab (score, why-now, signals, first touch,
contact→flow table) and the Reactivation tab (verdict, why it died, do-not-repeat, cycles, evidence).
👍/👎 and the copy button write back through the `record_feedback` serverless function — that feedback is
the loop, so `directives/self_improvement.md` applies to it.

**🚦 GATE.** A human reads the brief before the rep is asked to act on it. There is no automated quality
check yet, so this gate is the only thing standing between a bad analysis and a rep's inbox.

## Stage 1 — the signal run (built 2026-08-24)

The **delta layer** plus **all four** signal subagents.

```
per account:
  1. read the baseline   output/state/<domain>.json    (empty on first run)
  2. observe             four Agent calls IN ONE MESSAGE so they run concurrently:
                           s1-new-location · s1-leadership-hire · s1-open-jobs · s1-funding
                         each writes output/state/<domain>.<signal>.observed.json
  3. diff + merge        python3 scripts/state_snapshot.py diff <domain> \
                           --observation output/state/<domain>.new_location.observed.json \
                           --observation output/state/<domain>.leadership_hire.observed.json \
                           --observation output/state/<domain>.open_jobs.observed.json \
                           --observation output/state/<domain>.funding.observed.json
  4. score               hubspot-app/scripts/score_accounts.py
  5. write the email     Agent tool, subagent_type: ca1-first-touch
                         → output/briefs/<domain>.first_touch.json
  6. write to HubSpot    hubspot-app/scripts/upsert_brief.py  (the only write path)
  7. commit the baseline state_snapshot.py commit ...   (same --observation args)
```

Commit the baseline **last**, after the write succeeds. A crash before step 7 re-runs the account, which
is cheap; a crash after it would mean the signal was consumed but never delivered.

`ca1-first-touch` is `model: opus` while the hunters are `sonnet` — research is high-volume and
mechanical, composition is the one place quality is visible to a customer. It has **no web tools**, on
purpose: a search at composition time only invites an unverified fact into a rep's email. And it invokes
the `first-touch` **skill** rather than restating the formula, so the rules exist in exactly one place.
The performance-marketing repo records the failure mode this guards against — an agent that *named* a
skill without invoking it and improvised from a half-remembered version.

The four are **genuinely independent** — different sources, no shared context, no ordering between them —
which is precisely the shape Anthropic's guidance says multi-agent suits. Launch all four in a single
message; each account is then 4 concurrent workers, so keep concurrent *accounts* low.

**Why all four and not just the strongest.** The measured recall table (`_signal_stack.md`) reads as
though `new_location` is the only one worth having — 88% of detections, `funding` 0/80. That table
measured the **old detection**, before the 2026-08-12 fixes, and its own diagnosis says so: *"the events
happen; detection and windowing lost them"* — 16 real signals fell outside their window, 8 had no
publishable date, 8 were source-blocked. Post-fix evidence contradicts the pessimistic read: Portillo's
carries `new_location` + `leadership_hire` + `open_jobs` simultaneously and scores **100/high**. With
`new_location` alone the same account scores 86 — still `high`, but it loses the **8-day-old CFO hook
whose named remit lists the exact systems Nory replaces**, which is the best hook on the account. And
`hot_account` (3+ signals inside 30 days) is *structurally unreachable* with fewer than three agents.

`funding` earns its place even at 0/80 through the **quality of its negatives**: on Portillo's it checked
SEC/EDGAR and rejected a Feb-2024 synthetic secondary as not a funding event. That is an agent preventing
a false hook, which is worth as much as one finding a true one.

**The division of labour is the design.** The subagent OBSERVES — web research, and the judgement code
cannot make: `strength`, `stage`, `confidence`, `source_url`, `hook_detail`. `state_snapshot.py` DIFFS —
set differences, date arithmetic, expiry, `flagged_run`. Set maths and date maths are where an LLM
quietly gets things wrong, so they are code, and the subagent is given **no HubSpot tool at all** so the
write path staying deterministic is structural rather than aspirational.

**When the observer and the diff disagree about `present`, the diff wins** — a fact already in the
baseline is not a new signal — and the disagreement is reported in `note` rather than resolved silently.
This is the common case on a re-run: the observer correctly sees three sites, the diff correctly says none
of them is new.

Commit step 5 only after the score is written, so a crash between them re-runs the account rather than
losing the signal. The write is atomic (temp + `os.replace`), and a **corrupt baseline is fatal, never
treated as a first run** — silently starting over would re-flag the account's whole history.

**Two behaviours worth knowing before you read a result.**

*An incoming exec is the sharpest signal, not a data error.* An appointment is normally announced before
the person starts, so the differ measures from `announced_date` when present, and treats a **future**
`start_date` as age 0 rather than negative — flagging the name under `incoming`. Portillo's CFO was
announced Aug 4 effective Sep 7: dating from the start date gave age −14 and silently zeroed a strength-5
signal 8 days old.

*`present: false` is a real deliverable, especially from `funding`.* Most ICP accounts have no corporate
function to hire into and no capital event, so an evidenced negative — naming the board that was read,
or the filing that was checked and rejected — is what stops a rep opening on something that did not
happen. Do not treat an empty result as a failed run.

## Parallelism

At most **5 accounts in flight**. Bounded by HubSpot rate limits (measured: 190/10s, 19/s) and by bundle
size — median 15.7 KB but p90 161 KB and max 1.32 MB, which is more than a single context window. A
worker must never be handed a raw bundle above ~100 KB without slicing it first.

## Failure handling — the current weakness

Every script `sys.exit`s on the first HTTP error, so a batch is all-or-nothing: account 47 failing loses
48 onward. There is no checkpoint and `output/state/` has never been written. Until that changes, run
batches small enough to redo, and record which domains completed.
