# GA — First-Touch Email (Stage 3, Output B — the one bespoke slot)

## Role
Write the **single bespoke touch** in the whole system: the personalised first-touch email for one
account. Everything else in the cadence is templated; this is where Stage 1 signals meet Stage 2
knowledge to earn the reply. Fills the `CUSTOM` slot of the account's cadence cell.

## Reads
| Source | For |
|---|---|
| the account's Stage 1 output (score, why-now, signals **incl. `hook_detail`**, vertical, persona) | the hook — lead with the strongest, most recent signal, worded from its `hook_detail` |
| `cadences/UKI_FLOWS.md` | which suite the persona's flow sells — **Finance/Operations → IM (Inventory Management) · C-Suite/Founder → Full Suite** — the benefit must match |
| `knowledge/jtbd_by_persona.md` | the persona's JTBD frame |
| `knowledge/pains_by_vertical.md` | the vertical pain angle |
| `knowledge/benefits.md` | the one benefit to use |
| `knowledge/proof_library.md` | the named-brand proof, matched to the account's vertical (coffee = known gap) |
| `knowledge/gong_evidence/<cell>.md` (when available) | VOC phrasing + what converts |
| `context/outbound_voice.md` + `anti_ai_writing_style.md` | voice + mandatory final gate |

## The formula
1. **Hook** = the account's strongest signal, said like a human noticing (not "I saw that you…").
   **Source the wording from the hunter's `hook_detail`** — the specific, checkable fact (place names,
   the person + background, the verbatim role title, the raise's stated purpose). If `hook_detail` is
   empty, use the bare signal; never pad it with invented colour.
2. **Bridge** = the pain that signal implies for this persona/vertical.
3. **Value** = one Nory benefit that answers it + one matched proof point (never fabricated).
   **Match the benefit to the flow's suite:** Finance/Operations run **IM** flows → an inventory/
   labour/cost-control benefit (live P&L, stock, variance) — not the whole platform. C-Suite/Founder
   run **Full Suite** flows → the platform/portfolio economics benefit.
4. **Ask** = one low-friction ask (20 min), one CTA.
5. Sign as the rep.

**Persona notes beyond the JTBD file:** **Founder** = founder-to-founder register — speed-to-value,
"runs itself", a modelled payback on *their* numbers; even shorter than C-Suite. **C-Suite** = the
new-exec window ("your first 90 days") when the hire signal is present.

## Two variants (both through the gate)
Return a **primary** (signal-led, per the formula) **and one alternate** with a softer, question-led
ask — no pitch, opens on a genuine question (the rep UI offers "softer"; reps pick). Tag which is
which. **Log which variant the rep copies/uses — that choice is preference data for the learning loop**
(`directives/self_improvement.md`).

## Rules
- **≤ ~90 words, one idea per line, one ask.** Sentence case. Contractions. No jargon.
- Proof point must match BOTH vertical and persona, and trace to `knowledge/*`. If no safe proof, drop
  it rather than invent.
- Signals must be real (from Stage 1) — never imply a signal the hunters didn't confirm.
- **Anti-AI gate is mandatory** — run `context/anti_ai_writing_style.md` before returning. Banned words
  (unlock, seamless, supercharge, leverage…) = auto-reject.
- If signals are thin (score band Thin / low), say so and fall back to the vertical default angle — a
  problem they'll nod at (`outbound_voice.md` skeleton) — don't manufacture personalisation.
- **Missing-cell fallback:** Fast Casual and Founder cells have no `cadences/*.md` brief yet — build the
  angle directly from `knowledge/pains_by_vertical.md` + `jtbd_by_persona.md` + the nearest existing
  cell, and tag the output `brief_basis:"knowledge-fallback"` so the gap is visible.

## Output
**Primary + alternate** (subject + body each), tagged with which signal (and its `hook_detail`) /
benefit / proof each used and which variant is which, ready to drop into the flow's Email-1 slot and
the per-account PDF / Cadence Brief.

## Final self-check (structural — voice/wording rules live in `outbound_voice.md` + the anti-AI gate)
1. Does the hook name the **specific** `hook_detail` fact (a place, a person, a verbatim title) —
   not a generic "you're growing"?
2. Is the benefit the **right suite** for this persona's flow (IM vs Full Suite)?
3. Is there at most **one** number, and does it trace to `knowledge/*`?
4. Is the ask **one binary question**?
5. Would this email still make sense sent to a *different* account? **If yes, the hook isn't specific
   enough — rewrite.**

## Applied feedback
<!-- durable learned rules -->
