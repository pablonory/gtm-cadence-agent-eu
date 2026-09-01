# Full account refresh — reactivation + structured brief + conjunctural opener (one pass)

> Combined runbook for the 2026-08-13 batch over accounts with a dead deal. Each account gets ONE
> pass covering three things that used to be three separate runs. Read the referenced directives in
> full before writing anything — this file sequences them, it doesn't replace them.

You will be given: `domain`, `company`, `score`, `vertical`, `persona`, `locations`, `state`, `city`,
`needs_conjunctural` (bool). Do all of the following for that one account.

## Step 1 — Reactivation analysis (writes `reactivation_*` + `reactivation_json`)
Follow `directives/reactivation_deal_analysis.md` in full, start to finish:
```bash
python3 scripts/reactivation_bundle.py <domain> --company "<company>"
```
Read the bundle, decide evidence_basis, write the four long `reactivation_*` textareas AND the
structured `reactivation_json` (verdict/lead_with/hook/ask/do_not_repeat/why_it_died/cycles/evidence/
flags/call_detail/deal_detail/email_detail — exact shape and length-discipline rules are in that
directive's section 6b, don't skip it). Set `reactivation_analysis_date` = 2026-08-13 and
`reactivation_last_deal_url`.

## Step 2 — Decide `first_touch_basis` and, if thin, get a conjunctural opener
- If `needs_conjunctural` is **false** (a real Tier-1 signal fired and score ≥30): the existing
  first-touch copy is already grounded in an account signal. Set `first_touch_basis = account_signal`.
  Leave `first_touch_subject/body` as-is unless step 1 surfaced a `do_not_repeat` angle that the
  current copy actually uses — if it does, rewrite to drop that angle (see 2b).
- If `needs_conjunctural` is **true** (score <30 or no Tier-1 signal present in `signals_json`):
  run
  ```bash
  python3 scripts/conjunctural_match.py --nation <england|scotland|wales|ni|ireland> --vertical <vertical> --persona <persona> --locations <locations> [--council <council>] --json
  ```
  (Omit `--state` if none was given — the script will return no state-scoped matches, which is a
  valid outcome, not an error.)
  - **Match found, `usable_as_opener: true`**: rewrite `first_touch_subject`/`first_touch_body` (and
    the alt variant) to open on that conjunctural fact instead of the generic vertical-pain fallback.
    Follow `context/outbound_voice.md`'s skeleton and run the `context/anti_ai_writing_style.md` gate
    before finishing. Set `first_touch_basis = conjunctural` and
    `conjunctural_signal = "<id>: <title>"`. Update `first_touch_rationale` (and `copy_rationale` in
    step 3) to say the opener is conjunctural, not account-specific — don't launder it as a signal.
  - **No usable match**: keep the existing vertical-pain copy as-is. Set
    `first_touch_basis = vertical_pain`. Don't invent urgency.

### 2b. Reactivation take priority when the account has a dead deal
Every account in this batch has a dead deal — check step 1's `do_not_repeat` list before finalizing
first-touch copy either way. If the current `first_touch_subject/body` repeats an angle step 1 flagged
as already-tried-and-failed, rewrite the opener regardless of the account_signal/conjunctural/
vertical_pain basis. The reactivation finding always overrides a stale generic angle.

## Step 3 — Structure `brief_json` (what the Overview card renders)
Build/refresh the `brief_json` object (shape in `hubspot-app/scripts/upsert_brief.py`'s docstring):
```json
{
  "why_now": {"headline": "3-6 words", "points": ["one fact per bullet, max 4"]},
  "coordinate": {"owner": "rep name/email if known", "last_contacted": "YYYY-MM-DD or omit",
                 "days_ago": 123, "deals": "N (M dead)", "note": "one line, omit if nothing to flag"},
  "corrections": ["only real CRM/enrichment errors found this pass — omit array if none"],
  "copy_rationale": {"hook": "one clause", "proof": "one clause", "persona": "one clause",
                      "vertical": "one clause"}
}
```
Derive from whatever already exists on the brief (`why_now`, `first_touch_rationale`) plus anything
new from steps 1-2 — split existing prose into headline+bullets/clauses, don't just copy it in
wholesale. Omit any sub-object that would be empty padding.

## Step 4 — Write back
Single PATCH via `hubspot-app/scripts/upsert_brief.py` (it auto-loads `.env`, has `resolve_owner` etc.)
or a direct PATCH to the existing brief's properties — either is fine, this is a refresh not a create,
so match on `domain`. Include: the seven reactivation properties, `brief_json`, `first_touch_basis`,
`conjunctural_signal` (omit if `vertical_pain`/`account_signal`), and `first_touch_subject/body/
alt_subject/alt_body/rationale` only if step 2 rewrote them.

## Report back (per account)
One line: `domain — verdict=<x> basis=<x> conjunctural=<id or none> brief_json=written`.
If anything blocked (no company match, no deals found despite being in the dead-deal list, etc.),
say so plainly instead of forcing a result.
