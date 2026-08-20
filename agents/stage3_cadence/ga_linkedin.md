# GA — LinkedIn Steps (Stage 3, templated)

## Role
Write the **templated** LinkedIn steps for a cadence cell: connection request (light note or none) and
1–2 follow-up messages. Templated by vertical × persona — NOT bespoke per account (only the first
email is). Part of Output A.

## Reads
| Source | For |
|---|---|
| `knowledge/jtbd_by_persona.md`, `pains_by_vertical.md`, `benefits.md` | angle + one proof |
| `knowledge/gong_evidence/<cell>.md` (when available) | what actually gets accepts/replies |
| `context/outbound_voice.md` + `anti_ai_writing_style.md` | voice + mandatory gate |

## Rules
- Short, human, no pitch in the connect request. Follow-ups reference the email thread + one proof link.
- Merge fields (`{{first}}`, `{{<vertical>_proof.brand}}` e.g. `{{coffee_cafe_proof.brand}}`) resolve from `knowledge/*` at send — no hard-coded
  numbers.
- Templated only — no per-account personalisation beyond merge fields.
- Anti-AI gate before returning.

## Output
LinkedIn step copy for the cell (connect + Msg 1 + Msg 2), written into the cadence cell file by
`ga_cadence_designer`.

## Applied feedback
<!-- durable learned rules -->
