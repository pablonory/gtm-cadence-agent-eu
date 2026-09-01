# UKI Flows — cadence source of truth (⚠️ PLACEHOLDER — flows not yet confirmed)

> **Status (2026-08-20, Pablo):** the Gong flows UKI reps actually use are **unknown** — Pablo is
> still finding out what they run. This file is the placeholder that gets filled in when that
> investigation lands. Until then, the iron rule from the US fork applies with extra force:
> **NEVER invent a flow name.** The agent maps accounts to flows only when this file lists real,
> confirmed names.

## What the agent does UNTIL flows are confirmed

- Run Stages 1–3 normally (signals, score, classification, first touch) — none of that depends on flows.
- **Leave `cadence_template` and `gong_template_url` EMPTY** on every brief, and add one line to
  `why_now` / `brief_json.coordinate.note`: *"flow pending — UKI flow set not yet confirmed"*.
- Still classify vertical × persona (it aims the first-touch angle and the eventual mapping).
- `scripts/map_contacts.py` still groups contacts by persona; groups carry the persona label, no flow name.

## What to capture when investigating (the checklist for Pablo / the UKI owner)

The same facts we captured from Lewis's Gong for the US (screenshots of the flow folder worked well):

1. **Does a UKI flow folder exist in Gong?** Its exact name (US analogue: folder "US Flows").
2. **The exact flow names**, verbatim — the naming pattern may or may not match the US
   `<Vertical> × <Persona> (<Suite> · Tier 1)` convention.
3. **The matrix shape** — which verticals × personas have flows? Watch for UKI-specific cells the US
   matrix lacks (⚠️ **pubs & bars** is a major UK segment with no US cell).
4. **A reactivation motion?** (US analogue: "USA Reactivation".) Name assumed here as
   **"UKI Reactivation"** until confirmed — `hubspot-app/scripts/*` carry that assumption, flagged.
5. **Who owns the flows** (the UKI Lewis-equivalent) — they own territory + the input sheet too.
6. Per-flow: total people / active state (tells us what's actually in use vs built-and-abandoned).

## Inherited working assumption (candidate structure, NOT confirmed)

Carried over from the US fork so classification keeps working; every part below is provisional:

- **Verticals:** Coffee & Cafe · Fast Casual · FSR · QSR *(+ pubs & bars? — open question)*
- **Personas:** C-Suite · Finance · Founder · Operations
- **Suite from persona:** C-Suite & Founder → **Full Suite** · Finance & Operations → **IM**
- **Flow-name pattern:** `<Vertical> × <Persona> (<Suite> · Tier 1)` + a reactivation motion

## Classification rules (market-neutral — these ARE in force now)

**Vertical** — pick one:
- **Coffee & Cafe** — coffee groups, speciality coffee, all-day cafés, bakeries, brunch-led.
- **Fast Casual** — counter-order but elevated / fresh-prep, higher ticket than QSR, limited table service.
- **FSR** — full-service, sit-down, table service, larger menu + teams. *(UK gastropubs: currently FSR —
  revisit when the pubs & bars question is decided.)*
- **QSR** — quick-service, high throughput, often franchised.

**Persona:**
- **Founder** — founder-led / owner-operator; the founder is the buyer (usually fewer sites).
- **C-Suite** — hired executive (CEO / COO / CFO / MD) at a larger multi-site group.
- **Finance** — FD / Head of Finance / FC / Financial Controller.
- **Operations** — Ops Director / Head of Ops / Operations Manager.

> The key split is Founder vs C-Suite: founder-led / owner-operator = **Founder**; hired exec at
> scale = **C-Suite**. When the sheet's Persona is blank, default from HubSpot title + company size,
> and note the assumption in the brief.

Contact→flow mapping (`hubspot-app/scripts/map_contacts.py`) keeps the same persona priority:
Founder > C-Suite > Finance > Operations; unmatched titles are listed as **unmapped**, never guessed.

## Where the per-cell `cadences/*.md` files went

Removed 2026-09-01, following the US repo's removal (2026-08-24, cbb37d1): their day-by-day flow tables
were superseded by the real Gong flows, and their angle/proof content duplicated `knowledge/` — the
first touch is built straight from `knowledge/proof_library.md`, `knowledge/pains_by_vertical.md`,
`knowledge/jtbd_by_persona.md` and the conjunctural register, via `.claude/skills/first-touch/`.
The proof points were always UKI-native (£/€ results), so nothing UKI-specific was lost; the files
remain in git history (`952abff:cadences/`).
