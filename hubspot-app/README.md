# Nory Cadence Agent — HubSpot app (UKI fork: ⚠️ REFERENCE + SCRIPTS ONLY)

> **DO NOT `hs project upload` FROM THIS REPO.** The private app + the `cadence_brief` custom object
> are **shared across markets** and deployed **once, from the US repo**
> (`pablonory/gtm-cadence-agent`, portal 139694830, objectTypeId 2-251700583). Pablo's call
> (2026-08-10): briefs stay open portal-wide so EU/UKI reps use the same object. UKI briefs are rows
> on that shared object, distinguished by **owner** (UKI reps) + **`batch`** labels (`UKI batch N`).
>
> What this folder IS for, in this repo: `scripts/` (upsert_brief.py, score_accounts.py,
> map_contacts.py) — they operate on the shared object with the same `.env` token and work unchanged.
> Schema + card source here are reference copies; schema/card changes are made in the US repo and
> deployed from there (they serve both markets — e.g. the card's flow labels are market-agnostic).
>
> *If UKI ever needs a separate object* (different fields, separate permissions), the rename list is:
> project `name`, app `uid`+`name`, object `name` (e.g. `cadence_brief_uki`) + card `objectTypes`,
> function `uid`, and a second app install/token. Deliberately NOT done now — one object keeps
> reporting and the rep experience unified, which matches the EU-adoption intent.


The rep-facing surface from `prototypes/BUILD_SPEC.md`, as a real HubSpot developer project
(platform `2026.03`): a **static-auth private app** + the **Cadence Agent card** on the
`cadence_brief` custom object, plus the schema and the agent's write path.

```
hubspot-app/
  hsproject.json                      the project (platformVersion 2026.03)
  src/app/app-hsmeta.json             the private app: scopes, permitted URLs
  src/app/cards/                      the Cadence Agent card (React, @hubspot/ui-extensions)
  src/app/functions/recordFeedback.js writes rep_feedback / rep_feedback_detail / variant_copied
                                      (enum props whitelisted by value; rep_feedback_detail is free text,
                                      whitelisted by property + length instead — app token, server-side)
  schema/cadence_brief.schema.json    the custom object (BUILD_SPEC §A2 + softer-variant fields)
  schema/create_schema.py             creates it via /crm-object-schemas/v3/schemas (stdlib only)
  scripts/upsert_brief.py             the agent's upsert: owner from Rep email, assoc company/contact
  scripts/map_contacts.py             contact → flow map: every CRM contact on the company, classified
                                      by title into a persona and grouped under the exact flow to run
                                      (→ contacts_json + contact associations). Runs after the upsert.
```

> Why not an MCP Auth App: the remote MCP server has no custom-object support. Why not an
> app-object component: app objects need HubSpot approval (a request form) — the schema API works
> today on Enterprise. See `prototypes/BUILD_SPEC.md`.

## Deploy runbook (order matters — the app must exist before the schema script has a token)

**0. Prereqs** — Node 18+, `npm i -g @hubspot/cli`, then `hs init` (browser auth with a personal
access key, pick the Nory portal). Enterprise portal confirmed.

**1. Upload the project (creates the app).**
```bash
cd hubspot-app && hs project upload
```
First upload: expect a **validation pass/fail report** — the card's `objectTypes` placeholder is
invalid until step 3, so if validation blocks on it, temporarily set `"objectTypes": ["COMPANY"]`,
upload, and restore in step 4.

**2. INSTALL the app, then get its access token.** A static-auth project app has **no token until it
is installed**: Development → Projects → *nory-cadence-agent* → the app → **Install app** → approve
scopes. The access token (`pat-…`) then appears (install confirmation / the app's Auth tab). Verify
with `hs project app-install-status`. Store the token in the **gitignored env** (same place as
`GONG_ACCESS_KEY`):
```bash
export HUBSPOT_PRIVATE_APP_TOKEN=pat-...
```

**3. Create the custom object.**
```bash
python3 schema/create_schema.py
```
Prints `objectTypeId` (e.g. `2-12345678`) and `fullyQualifiedName` (e.g. `p1234567_cadence_brief`).
Idempotent — re-running reports instead of duplicating.

**4. Point the card at the object + re-upload.** The card's `objectTypes` uses the **portal-agnostic**
form **`p_cadence_brief`** (NOT the full `p<portalId>_…` FQN — the validator rejects that). Already set
in `src/app/cards/cadence-brief-card-hsmeta.json`. `hs project upload` again. (API calls, by contrast,
use the `objectTypeId` — `upsert_brief.py` resolves it automatically.)

**5. Add the card to the record layout (one-time, manual).** Open any Cadence Brief record →
**Customize** → middle-column tab → **+ Add card** → filter *App* → **Cadence Agent** → save.

**6. Access control (portal admin — the whole point).** Settings → Users & Teams:
   - **Team `US Sales — AE`** — the US AEs; primary team.
   - **Permission set `US Cadence — AE`** — assigned ONLY to US AEs:
     Cadence Brief **View ✓ / Edit ✓ / Delete ✕**, record scope **Owned only**.
   - **Permission set `US Cadence — Manager`** (Lewis): **Team**-level view, no edit.
   - Everyone else: no access to the object — the card, list views, and records don't exist for them.
   - **Verify with two test users** (one US AE, one non-US) before adding real data.

**7. Saved view = the queue.** CRM → Cadence Briefs → filter `Cadence Brief owner = me`, sort
Score ↓, save as **"My cadence targets"** (shared with the team; scoping makes it per-rep).

**8. Smoke-test the write path.**
```bash
python3 scripts/upsert_brief.py test_brief.json   # a fictional account, owner = a test rep
```
Then check: the record exists, is owned by the test rep, associated to a company, and the card
renders score/signals/first touch. Delete the test record after.

## What the agent writes (pipeline hand-off)

The pipeline (Stage 3) emits one JSON per account — shape documented at the top of
`scripts/upsert_brief.py` — and calls the script (or replicates its calls). Rules it enforces:
- `rep_email` must resolve to a HubSpot owner, or it **fails loud** (a typo orphans the cadence).
- Upsert key = `domain` (unique on the object). No duplicate briefs per account.
- `cadence_template` must match the flow naming pattern (`cadences/UKI_FLOWS.md`) — warned if not;
  while UKI flows are unconfirmed the correct value is EMPTY ("flow pending").
- `batch` carries the input-run label from the sheet's Batch column (free text, e.g.
  `Reactivation US batch 1/6`) so briefs stay filterable by the upload they arrived in. Warned if missing,
  never invented — an unlabelled brief is valid, just harder to find later.
- `first_touch_basis` records what the opener was built on: `account_signal` when Stage 1 found something
  specific to them, `conjunctural` when `score_accounts.py` flagged `needs_conjunctural` (score under
  `CONJUNCTURAL_THRESHOLD`, or zero present signals) and `scripts/conjunctural_match.py` returned a
  quantified industry/macro fact, or `vertical_pain` when neither applies and the copy falls back to
  `knowledge/pains_by_vertical.md`'s generic default angle. `conjunctural_signal` names which register
  entry was used. See `knowledge/conjunctural/README.md` — this is an explicit, unproven experiment;
  recording the basis is what lets the feedback loop eventually tell us whether it beats the fallback.

After the upsert, the pipeline runs `scripts/map_contacts.py <domain>` — it pulls **all** contacts
associated with the HubSpot company, classifies each job title into Founder / C-Suite / Finance /
Operations (priority order Founder > C-Suite > Finance > Operations; rules in `cadences/UKI_FLOWS.md`),
groups them under the exact flow name for the account's vertical, writes the result to
`contacts_json`, and associates every mapped contact to the brief. Titles that match no persona (GM,
IT, marketing…) are listed as `unmapped` — shown to the rep, never guessed. This is what makes MM/ENT
accounts multithreadable: one brief, several flows, each aimed at the right people.

## v2 (not in this build)
- **Ask-the-agent chat in the card** — needs a live agent endpoint; the card is ready for a
  `hubspot.fetch` → backend hookup (add the URL to `permittedUrls.fetch`).
- **Signals as a child object** instead of `signals_json` (BUILD_SPEC §A3).
- Dev loop: `hs project dev` gives hot-reload against a test account.

## Deploy status (verified live on nory-prod, 2026-08-10)
- ✅ App deployed (build #3) + installed; token in the gitignored `.env`.
- ✅ `cadence_brief` created — objectTypeId `2-251700583`, FQN `p139694830_cadence_brief`.
- ✅ Card renders on the object; **Copy email**, 👍/👎 (`hubspot.serverless` → `record_feedback` →
  `PRIVATE_APP_ACCESS_TOKEN` PATCH), and the softer-variant toggle all confirmed working.
- ✅ **👎 opens a free-text detail box** (2026-08-13) — "what was off?" written to `rep_feedback_detail`.
  This is the highest-value input to the learning loop: a thumbs-down alone says a draft was wrong, the
  detail says *why* (wrong signal, wrong persona, wrong tone, stale hook, live-thread collision…).
  Round-trip write/read verified.
- ✅ Write path smoke-tested end-to-end: create → idempotent update (domain key) → owner resolution
  from rep email → read-back. Test record archived after.
- ⏳ Still theoretical: the v4 `/associations/default/` company association (test domain matched no
  company by design) — verifies on the first real account.
- ⏳ Remaining setup: saved view (step 7).
- **Permissions decision (Pablo, 2026-08-10): Cadence Briefs stay OPEN to all portal users for now** —
  EU reps may adopt it too. The step-6 lockdown (US-only permission set + owned-only scoping) is
  designed and documented above; apply it later if/when access needs tightening.
