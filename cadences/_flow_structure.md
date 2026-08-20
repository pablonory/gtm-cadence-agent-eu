# Shared cadence flow structure

> The default touch sequence every cell inherits unless a vertical/persona needs a different rhythm.
> `ga_cadence_designer` starts here, then adapts per cell. This file is the shared structural reference
> every cell inherits (e.g. `fsr_finance.md`, `coffee_cafe_finance.md`) — no single cell is "the shape".
> **Refresh rule:** when `ga_gong_sequence_analyst` has real data, the best-performing rhythm from Gong
> overrides this default (with Lewis's sign-off).

## Defaults
- **Length:** ~19 business days.
- **Touches:** 14 (team's own learning was 16 vs the old 8 — tune per Gong evidence).
- **Channels:** multi-channel — email × call × LinkedIn (+ 1 voicemail). No channel runs alone.
- **Bespoke slot:** only **Email 1** is `CUSTOM` (per account). Everything else is templated by cell.

## Default sequence (inherit unless overridden)

| Day | Channel | Touch | Purpose |
|----|---------|-------|---------|
| 1 | Email | Email 1 | **`CUSTOM`** — bespoke first touch (signals × knowledge) |
| 1 | LinkedIn | Connect | connection request, no/light note |
| 2 | Call | Call 1 | templated opener |
| 3 | Email | Email 2 | templated — primary pain angle |
| 4 | Call | Call 2 | templated |
| 6 | LinkedIn | Message 1 | templated — reference the email + one proof |
| 8 | Call | Call 3 + VM | templated + voicemail |
| 9 | Email | Email 3 | templated — proof point |
| 11 | Call | Call 4 | templated |
| 13 | Email | Email 4 | templated — case study |
| 15 | LinkedIn | Message 2 | templated — nudge + proof link |
| 17 | Call | Call 5 | templated |
| 19 | Email | Email 5 | templated — breakup |

Channel mix: **5 email · 5 call · 3 LinkedIn · 1 voicemail**.

## When to deviate (say why in the cell)
- **C-suite** — shorter, higher-altitude, fewer touches (they won't read 5 emails). Compress to ~10.
- **SMB / owner-operator (2–9 sites)** — US deals here close fast (**~12–15 days**, often same-day inbound;
  see `context/icp/segments.md`). Solo decision-maker → run a **compressed, punchy** cadence pushing a quick
  yes; the full 19-day / 14-touch flow may over-run them.
- **Mid-market (10–29 sites)** — longer cycle (~18–22 days, 45–55 for pilots) + more stakeholders → the
  **full multi-threaded cadence** fits.
- **Vertical rhythm** — if Gong shows a cell converts on a different cadence, follow the evidence.

## Non-negotiables
- Every step's copy passes the anti-AI gate (`context/anti_ai_writing_style.md`).
- One proof point per message, matched to vertical AND persona; merge fields resolve from `knowledge/*`
  at send — never a hard-coded/fabricated number.
- The agent designs; **Lewis builds the template in Gong once**; the rep assembles + activates.
