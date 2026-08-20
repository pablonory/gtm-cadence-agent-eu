# Cadence template — Coffee/Café × Ops

> Output A. One of the main-vertical cadence cells. **All main verticals — Coffee/Café · QSR · FSR — are
> equal-priority targets; none is "the focus".** Shared structure lives in `_flow_structure.md`; this
> cell adds the Coffee/Café × Ops angle, proof, and copy. Coffee/Café is **proof-light** — no hard coffee
> outcome number exists yet — so this cell leans on forecasting-accuracy + the US coffee logo cluster,
> never a fabricated %. Lewis builds it as a Gong template once; per account the agent fills only the
> `CUSTOM` first-touch email and points the rep here.

| | |
|---|---|
| **Targets** | Ops Director / Head of Ops / Operations Manager at multi-site coffee & café groups (core 5–29 sites) |
| **Goal** | Book a 20-min discovery — **offer to rebuild one site's week** (rota + order) off the forecast instead of by hand |
| **Length** | Full multi-thread (MM cycle ~18–22 days): ~19 business days, 14 touches (5 email · 5 call · 3 LinkedIn · 1 VM), inherits `_flow_structure.md` |
| **Angle** | Rotas and stock orders built by hand, site by site, every week — hours that aren't profit-leading, and the till still doesn't talk to the labour system. On coffee's AM peaks that manual guess is where labour % leaks |

**Persona brief (from `knowledge/`, shown to the rep at the top):**
A multi-site coffee/café ops lead is measured on labour cost %, GP per site, consistency site-to-site,
and admin hours. Pain: rotas and orders rebuilt manually in Excel (or "GPT sheets") for every site, the
till not feeding the labour system, and no single view until month-end — "a waste of my time, it's not
profit leading." Nory's answer: rotas and ordering built off a live ~97% demand forecast, one view
across every site, so GMs get the floor time back. Proof is forecasting-accuracy + the US coffee logo
cluster (never a fabricated coffee number — see `proof_library.md`).

## Discovery goals (probe on the first live conversation — not in the cold email)
- **Incumbent + contract end date** — contract expiry is the #1 compelling event (`_signal_correlation.md`).
- **POS / till fit** — confirm the till actually feeds the labour system (the "till talking to labour" pain);
  a POS mismatch is a common DQ.
- If on **XtraChef / an inventory-first tool** → lead the displacement story (`proof_library.md` US section).

## Flow
Inherits the default 14-touch sequence from `_flow_structure.md` (Email 1 = `CUSTOM`, rest templated).

## Copy
*(All copy in `context/outbound_voice.md` — human 1:1, plain, one binary ask. Anti-AI gate before use.)*

### Email 1 — Day 1 — `CUSTOM` (agent generates per account)
Example for an account with signals *3 new cafés this quarter + an open Ops Manager role*:
> **Subject:** 3 new cafés + an ops hire
>
> Hi {{first}} — saw you've opened 3 cafés this quarter and you're hiring an ops manager. That's usually
> the point where rota-building and stock orders turn into a manual job across every site, done in a
> spreadsheet on a Sunday.
>
> We build both off a live demand forecast (~97% accurate), so the AM peak is staffed to actual covers,
> not a guess, and it's the same view for every site.
>
> Worth 20 minutes? {{rep_first}}

### Email 2 — Day 3 — templated (the manual-time angle)
> **Subject:** building rotas by hand
> Hi {{first}} — most multi-site coffee ops leads I speak to are still building rotas and orders in a
> spreadsheet, site by site, and say the same thing: it's hours that aren't profit-leading. Nory builds
> both off a live forecast so your GMs get that time back on the floor. Worth a quick look? {{rep_first}}

### Email 3 — Day 9 — templated (proof)
> ⚠️ **Coffee/Café proof gap:** `knowledge/proof_library.md` has **no hard coffee labour/GP number** yet
> (Black Sheep figures unpublished). For this cell, resolve `{{coffee_cafe_proof.*}}` to the
> **forecasting-accuracy** proof (~97%) and/or the **US coffee logo cluster** ("four US coffee groups") —
> or a milk-COGS proof (UK — lead with the story, model the prospect's $) **only if the pain is GP/over-ordering**. Never invent a coffee %.
>
> **Subject:** how accurate is the forecast?
> Hi {{first}} — the fair question with anything automated is whether the forecast's actually right.
> Ours runs {{coffee_cafe_proof.forecast_accuracy}} against actuals, and we're already live in
> {{coffee_cafe_proof.cluster}}. That's what makes the rota trustworthy enough to stop hand-checking
> it. Worth 20 min? {{rep_first}}
> *(merge fields resolve from `proof_library.md`, matched to Coffee/Café — never fabricated)*

### Email 4 — Day 13 — templated (the concrete offer — one site rebuilt)
> **Subject:** your next week, built from the forecast
> Hi {{first}} — rather than pitch, we can take one site and show next week's rota and order built off our
> forecast instead of by hand: you see the covers we predict and the hours it saves before you commit to
> anything. Want us to run one? {{rep_first}}
> *(the ops parallel to Finance's Labour Assessment — Ops responds to hours-back + fast proof, not a $ model.)*

### Email 5 — Day 19 — templated (breakup)
> **Subject:** closing the loop
> Hi {{first}} — haven't caught you, so I'll assume getting the manual rota and ordering work off your team
> isn't a priority this quarter and close this out. If that changes as the new sites ramp, I'm one reply
> away. {{rep_first}}

### LinkedIn Msg 1 — Day 6 — templated
> Hi {{first}} — reached out by email too. We help multi-site coffee ops leads stop building rotas and
> orders by hand — both run off a live forecast, same view for every site. Given you're scaling, thought
> it might land. Open to connecting?

### LinkedIn Msg 2 — Day 15 — templated
> Short nudge + one proof link (Coffee/Café — forecasting accuracy or US cluster).

### Call 1 opener — Day 2 — templated
> "Hi {{first}}, {{rep}} from Nory — I'll be quick. I work with ops leads at coffee groups your size who
> are still building rotas and stock orders by hand, site by site, in a spreadsheet. Is that fair, or have
> you already got that off your plate?"

### Voicemail — Day 8 — templated
> "{{first}}, {{rep}} at Nory — chasing my email on getting the manual rota and ordering work off your
> team, built off a forecast instead. Worth a look given the new openings. I'll try you Thursday, or reply
> to my email."

---
*Grounded in `knowledge/jtbd_by_persona.md` (Ops JTBD — hours back, control at scale), `gong_evidence/_voc.md`
(Ops language — "waste of my time, not profit leading", GPT sheets, till not talking to labour),
`_objections.md` (#5 GM-judgment: Nory gives better inputs, GM still calls it), and `context/outbound_voice.md`.
⚠️ Coffee/Café is proof-light — this cell cannot lead with a quantified coffee win (unlike FSR); it leans on
~97% forecast accuracy + the US coffee logo cluster until real coffee numbers land. Rhythm is best-practice,
not yet Gong-tuned (`_sequence_performance.md`).*
