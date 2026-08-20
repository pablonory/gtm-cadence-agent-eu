# Input — the accounts sheet (UKI)

The v1 entry point is a **Google Sheet**, one row per account, keyed by rep. The **UKI territory
owner** (⚠️ TO CONFIRM — the Lewis-equivalent; see `CLAUDE.md`) owns it and controls territory; the
agent reads it, groups by rep, and runs the 3 stages per account.

> ⚠️ **The UKI sheet does not exist yet.** Create it to the schema below (copy the US template's
> structure, NOT its data). Never reuse the US sheet — different territory, different owner.
> Never commit a local export of real prospect data (see `.gitignore`).

## Sheet schema

The owner fills the left block; the agent writes the right block back.

| Column | Who fills | Notes |
|---|---|---|
| **Rep (email)** | owner | must match the rep's Gong/HubSpot user — this attributes the cadence + digest |
| **Batch** | owner | free-text label for this import/run, e.g. `UKI batch 1`. Written to `batch` on the Cadence Brief so briefs can be filtered/grouped by run (and distinguishes UKI rows on the shared object) |
| **Company** | owner | |
| **Domain** | owner | research + dedup key; agent derives it if blank |
| **Vertical** | owner | dropdown: Coffee & Cafe / Fast Casual / FSR / QSR — pending the pubs & bars decision (`cadences/UKI_FLOWS.md`) |
| **Persona** | owner | dropdown: C-Suite / Finance / Founder / Operations — **optional**; sets the *primary* persona. The agent also maps every CRM contact by title (`map_contacts.py`). Blank → agent defaults from title + company size |
| **Locations** | owner | segment / scoring input |
| Status | agent | `Queued → Scored → Brief ready` (or `Error: …`) |
| Score | agent | overall account score |
| Why-now | agent | one-line summary |
| Brief link | agent | link to the Cadence Brief record in HubSpot |
| Last run | agent | for dedup / suppression |

## Rules
- **Rep = real work email**, validated against the HubSpot owner list — a typo orphans the cadence
  (`upsert_brief.py` fails loud on this, by design).
- The sheet is **territory control**; HubSpot is the **data** (agent matches on domain to enrich).
- Dedup: skip rows processed inside the suppression window unless a `Force` flag is set.
- Until `cadences/UKI_FLOWS.md` is confirmed, briefs are written **without** a flow name ("flow
  pending") — the sheet still fills, scoring still runs.
- Graduation path (same as US): move the entry point to a HubSpot active list once the loop is proven.
