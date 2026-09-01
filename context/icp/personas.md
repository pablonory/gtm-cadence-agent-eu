# Personas — the cadence matrix (columns)

> Second axis of the Stage 3 matrix (rows = `verticals.md`). The **Persona** column in the accounts
> sheet picks the column; Vertical × Persona picks the cadence cell. Grounded in the three buyer
> personas in the paid-media repo's `business_profile.md` (external source — not in this repo; its facts
> are distilled into `context/product/product.md` here), mapped onto the three outbound personas Lewis uses.

## The four outbound personas (market-neutral — inherited unchanged at the UKI fork)

> Four cells, not three: **Founder** is split out from **C-Suite** (see below). The persona also fixes the
> product **suite** in the flow name — Finance & Operations → **IM** (Inventory Management); C-Suite &
> Founder → **Full Suite**. Full matrix: `cadences/UKI_FLOWS.md`.

### Operations — "the operator" (Ops Director / Head of Ops / Operations Manager)
- **Owns:** P&L delivery across sites, labour & rota, supply chain, consistency site-to-site, team
  retention. Part of the buying committee; often the champion.
- **Measured on:** labour cost %, GP per site, consistency across venues, hours lost to admin.
- **Pain:** fragmented systems, no single source of truth, inconsistent profitability across venues,
  15 hrs/week on admin, can't see what's leaking until month-end.
- **What lands:** portfolio-scale control, consistency, hours back, low-effort rollout, fast proof.
- **Maps to `business_profile` Persona 1** (Multi-Unit Operator / Ops Director). → **Operations (IM · Tier 1)** flow.

### Finance — "the numbers owner" (Finance Director / Head of Finance / FC / Financial Controller)
- **Owns:** margin, month-end close, forecasting, cost control, board reporting.
- **Measured on:** prime cost %, margin per site, close speed, forecast accuracy.
- **Pain:** labour % and COGS visible only in arrears (month-end), forecasting is gut-feel, every new
  site multiplies blind spots, prime-cost leakage (£60K–120K lost per £1M revenue/yr on 3–5% margins).
- **What lands:** live P&L per site, catch drift the week it happens, quantified payback, variance
  control. **Proof-led — always pair a claim with a named brand + number.**
- Built example briefs for this persona: `cadences/fsr_finance.md`, `cadences/coffee_cafe_finance.md`. → **Finance (IM · Tier 1)** flow.

### C-Suite — "the growth owner" (**hired** CEO / COO / CFO / MD at a larger multi-site group)
- **Owns:** growth strategy, unit economics, expansion, investor story.
- **Measured on:** net profit, growth rate, ability to scale without losing margin discipline.
- **Pain:** scaling rapidly without margin erosion, reliance on luck vs systems, patchwork of tools
  that won't scale, thin net margins under rising costs + flat demand.
- **What lands:** the category POV (control vs luck, "No profit lost"), portfolio economics, the
  strategic bet, peer/investor proof (funding, tier-1 logos). Shortest, highest-altitude cadence.
- → **C-Suite (Full Suite · Tier 1)** flow.

### Founder — "the owner-operator" (Founder / Owner where the founder IS the buyer)
- **Split from C-Suite (2026-08-10)** because Lewis runs a distinct Founder flow. Use when the business is
  **founder-led / owner-operator** — typically fewer sites, the founder holds the P&L and the decision.
- **Owns:** everything — the P&L, the vision, and the day-to-day; buys fast, on conviction + payback.
- **What lands:** speed-to-value, "runs itself", a quick modelled payback, founder-to-founder proof.
- **Founder vs C-Suite is the key split:** founder-led / owner-operator = **Founder**; hired exec at a
  larger group = **C-Suite**. Default from HubSpot title + company size when the sheet is blank; note it.
- → **Founder (Full Suite · Tier 1)** flow.

## The GM / site-manager note
`business_profile` Persona 2 (GM / site-level manager) is an **end user + adoption influencer, rarely
the buyer** — not a standalone outbound persona. Don't target a GM as the primary cadence contact;
they surface as a multithreading touch inside an Ops or Finance cadence when useful.

## Who actually buys — US-fork pipeline evidence (directional, LOW confidence; UKI read TBD)
> From the active US pipeline (sales-intel app, 2026-07-17). **Caveat:** no rolled-up call volume or
> closed-won-by-persona attribution exists — this is the *shape* of the pipeline, not measured
> conversion. RevOps gap: contact-role fields (first-touch vs economic buyer vs champion) aren't
> consistently populated. Don't treat as proven.

- **Ops / owner-operator** (VP Ops, Operations Director, Owner) tend to drive the **early discovery** calls.
- **Finance** (CFO, Director of Supply Chain, Finance lead) shows up on **high-value, later-stage** deals
  (Demonstration / Negotiation) → the economic validation seat.
- **Both US closed-won deals to date were owner-led** (Heirloom Group, Ark Restaurants) — but two deals
  is far too thin to generalise, especially for SMB where the owner *is* the C-suite.

**Design implication — the buying-committee sequence:** **Ops opens → Finance validates → Owner/C-suite
decides.** This is why we multi-thread: enter via Ops (discovery/champion), but make sure Finance (the £/$
economic case) and the Owner/C-suite (decision, especially SMB owner-operator) are engaged too. Pairs with
the **8%→39% booking-rate multithread stat** (`knowledge/gong_evidence/_sequence_performance.md`): aim for
≥3 stakeholders per account across these seats.

## How the persona is used
- Sheet `Persona` dropdown → **C-Suite / Finance / Founder / Operations**. **Optional** — if blank, the
  agent defaults from the contact's title in HubSpot + company size (see `hubspot-app/scripts/score_accounts.py`
  classification), and notes the assumption. Persona also fixes the **suite** in the flow name
  (Finance/Operations → IM; C-Suite/Founder → Full Suite).
- Selects the matrix column → the matching **UKI flow** (`cadences/UKI_FLOWS.md`, pending) and the JTBD brief
  (`knowledge/jtbd_by_persona.md`).
