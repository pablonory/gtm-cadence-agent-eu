# Build spec — Cadence Brief in HubSpot (rep-facing UI)

How to turn `prototypes/hubspot_cadence_object.html` into the real thing. Tier assumed: **Enterprise**
(custom objects + permission sets confirmed available). Nothing here sends outbound — the agent writes
briefs; reps read them and assemble/activate in Gong.

Two tracks: **(A)** build the HubSpot surface, **(B)** wire the agent's writes. Plus **(C)** access control.

---

## 0. Cadence source of truth — Lewis's Gong "US Flows"

The agent does **not** design cadences. It maps each account to a **ready-built flow in Gong's `US Flows`
folder** (owned by Lewis) and references it by exact name. Matrix = **4 verticals × 4 personas = 16 flows**
(all Tier 1), plus a **USA Reactivation** motion.

- **Verticals:** Coffee & Cafe · Fast Casual · FSR · QSR — *Fast Casual is its own vertical here; this
  supersedes the "casual → FSR" rule in `context/icp/verticals.md`.*
- **Personas:** C-Suite · Finance · Founder · Operations — *Founder is distinct from C-Suite.*
- **Suite is derived from persona:** C-Suite & Founder → **Full Suite**; Finance & Operations → **IM**.
- **Flow-name pattern (exact):** `<Vertical> × <Persona> (<Suite> · Tier 1)`, e.g. `Fast Casual × Finance (IM · Tier 1)`.
  Store this verbatim in `cadence_template` so the rep opens the right one.

> **Consequence:** Stage 3 Output A collapses from "design a cadence library" to "select the matching US
> Flow". The `cadences/*.md` cells we authored (9, 3×3) are superseded by these 16 named flows — realign
> or retire them. Confirm the Founder-vs-C-Suite and vertical classification rules before wiring (see G).

---

## A. The `Cadence Brief` custom object

One record per (account × run) that the agent owns end-to-end.

### A1. Object definition
Create via `POST /crm/v3/schemas` (or in the developer Project config).

- **Object name (internal):** `cadence_brief`
- **Primary display property:** `company_name`
- **Secondary display:** `score`, `status`
- **Associated objects:** `COMPANY` (required), `CONTACT` (the persona contact), optional `DEAL`
- **Enable owners:** yes — records carry `hubspot_owner_id` (this is what record-scoping keys on)

### A2. Properties

| Internal name | Type / fieldType | Notes |
|---|---|---|
| `company_name` | string / text | primary display; mirrors associated company |
| `domain` | string / text | dedup key |
| `score` | number / number | 0–100 overall account score |
| `status` | enumeration / select | `queued` · `scored` · `ready` · `in_cadence` (matches sheet lifecycle) |
| `vertical` | enumeration / select | `coffee_cafe` · `fast_casual` · `fsr` · `qsr` (matches Lewis's US Flows) |
| `persona` | enumeration / select | `csuite` · `finance` · `founder` · `operations` |
| `locations` | number / number | site count / segment input |
| `why_now` | string / textarea | one-line angle |
| `signals_json` | string / textarea | **v1:** JSON array of `{type,title,detail,date,source_url,strength}`. See A3. |
| `first_touch_subject` | string / text | bespoke Email 1 subject |
| `first_touch_body` | string / textarea | bespoke Email 1 body |
| `first_touch_rationale` | string / textarea | which signal/benefit/proof it used |
| `evidence_backed` | bool / booleancheckbox | true = Gong-backed; false = positioning-only |
| `cadence_template` | string / text | **exact** Gong US Flow name, e.g. `FSR × Finance (IM · Tier 1)` — see §0 |
| `gong_template_url` | string / text | deep link to Lewis's US Flow in Gong |
| `anti_ai_passed` | bool / booleancheckbox | gate result |
| `last_run` | datetime / date | dedup / suppression |
| `rep_feedback` | enumeration / select | `up` · `down` · `none` — writes back to the learning loop |

`hubspot_owner_id` is standard (not listed above) and is set per record — see B3.

### A3. Signals — v1 vs clean
- **v1 (ship first):** `signals_json` as a JSON string; the card parses and renders the table.
  Fastest, no extra object.
- **Clean (later):** a child `cadence_signal` custom object (1 brief → many signals), associated to the
  brief. Better for reporting/filtering on signal type. Not needed for v1.

---

## B. Agent → HubSpot (the write path)

### B1. Auth — Private App (not MCP Auth App)
The remote MCP server doesn't expose custom objects, so the agent uses a **Private App** token against
the CRM API. Store the token in the gitignored env (same pattern as `GONG_ACCESS_KEY`).

**Scopes:**
- `crm.schemas.custom.read` (+ `crm.schemas.custom.write` only if the agent creates/edits the schema)
- `crm.objects.custom.read`, `crm.objects.custom.write`
- `crm.objects.companies.read`, `crm.objects.contacts.read`
- `crm.objects.owners.read` (resolve rep email → owner id)

### B2. Endpoints
- Upsert brief: search by `domain` + suppression window → `POST /crm/v3/objects/cadence_brief`
  (create) or `PATCH …/{id}` (update). Search: `POST /crm/v3/objects/cadence_brief/search`.
- Associate to company/contact: `PUT /crm/v4/objects/cadence_brief/{id}/associations/company/{companyId}/{assocTypeId}` (same for contact).
- Resolve owner: `GET /crm/v3/owners?email=<rep email>` → `hubspot_owner_id`.

### B3. Owner attribution (the linchpin)
For every brief, set `hubspot_owner_id` = the owner id resolved from the **input sheet's Rep column**.
This single field is what makes record-scoping (C2) attribute each brief to the right rep. A typo /
unresolved email = an orphaned brief → validate before write (fail loud, don't guess).

### B4. Where the pipeline writes
Slots into the existing Stage 3 hand-off: instead of (or alongside) the Drive PDF, the agent writes/
updates one `cadence_brief` record per account with the fields above, sets owner + associations, and
flips `status`. Weekly digest can query the object grouped by owner.

---

## C. Access control — US reps only + owner-scoped

Two independent layers, both server-side. Neither is bypassable from the browser.

### C1. Layer 1 — object gate (US Sales only)
Settings → Users & Teams → **Permission Sets** → create `US Cadence — AE`:
- `Cadence Brief`: **View ✓, Edit ✓, Delete ✕**
- Record scope on the object: **Owned only**
- Assign to the US AE users only. Anyone without this set has **no access** to the object (card + list
  view + records simply don't exist for them — UK reps, Marketing, CS).

### C2. Layer 2 — record scope (own briefs)
Settings → Users & Teams → **Teams** → `US Sales — AE`; reps' primary team. Combined with "Owned only",
each rep sees only briefs where `hubspot_owner_id` = them.
- **Manager (Lewis):** a separate `US Cadence — Manager` set with **Team**-level *read* (coaching), **no
  edit/launch**.

### C3. Not to conflate
The agent's Private App token can write briefs for **all** reps — that's fine and expected. The US-only
+ per-rep isolation is enforced on the **human** users via C1/C2, never via the agent's credential.

---

## D. UI Extension card (`@hubspot/ui-extensions`)

Built in the developer **Project**; renders on the `cadence_brief` record page (middle column).

- **Reads** the record's own properties (score, why_now, signals_json, first_touch_*, cadence_*).
- **Components:** `Statistics`/`ProgressBar` (score), `Tag` (vertical/persona/status), `Table` (signals),
  `Text`/`Tile` (email), `Button` (Copy email, Open in Gong, thumbs), `Input` (ask-the-agent).
- **Serverless function** (`hubspot.fetch`) backs: "Redraft/softer", the ask-the-agent chat, and thumbs
  → posts back to the agent + writes `rep_feedback`. Copy-email is client-side clipboard.
- **Queue = list view:** a saved view on `cadence_brief`, filter `Cadence Brief owner = me`, sort `score`
  desc, saved as **"My cadence targets"**. This is native — no build.

---

## E. Build order

1. Define `cadence_brief` schema (A) + properties + associations + enable owners.
2. Create the Private App (B1); confirm scopes; drop token in env.
3. Teach the pipeline to upsert briefs with owner + associations (B2–B4).
4. Permission set + teams (C) — with a test US rep and a non-US test user to prove the gate.
5. UI Extension card + serverless function (D); save the "My cadence targets" list view.
6. Verify: a US rep sees only their briefs; a non-US user sees nothing; Lewis sees the team read-only.

## G. Open decisions
- **Vertical classification:** how does the agent decide Fast Casual vs FSR vs QSR vs Coffee & Cafe?
  (Needs a rule now that Fast Casual is its own cell — supersedes `verticals.md`.)
- **Founder vs C-Suite:** the rule for routing to the Founder flow vs the C-Suite flow (owner-operator /
  founder-led vs hired exec at larger groups?).
- Confirm **"IM"** expansion (Inventory Management?) — affects the first-touch benefit framing for
  Finance/Operations flows.
- Realign or retire `cadences/*.md` (9 cells) against Lewis's 16 US Flows — §0.
- **USA Reactivation:** is re-engagement in scope for v1, or matrix flows only?
- Signals as `signals_json` (v1) vs child object (later) — A3.
- Keep the Drive PDF in parallel during rollout, or cut over to the object immediately?
- Does the ask-the-agent chat call the live agent, or a cached last-run response? (Latency vs freshness.)
