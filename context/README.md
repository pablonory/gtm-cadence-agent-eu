# Context

Standing inputs the agents read. Brand/product-specific (this is the Nory instance).

## product/
Source material for Stage 2a product knowledge: what Nory does, modules, features, integrations,
pricing where relevant. Distilled into `knowledge/product.md`.

## icp/
- The vertical definitions (Coffee, Cafe, QSR, Full-service — and whether "Casual" is a 5th).
- The persona definitions (Ops, Finance, C-suite): titles, what they own, how they're measured.
- Segment thresholds (location bands) used for scoring/routing.

## Voice files
- `outbound_voice.md` — how a **real rep** sounds in 1:1 outbound. Purpose-built for human sales
  email/LinkedIn/calls — explicitly **NOT** Nory's marketing brand voice (no slogans, puns, or ad
  copy). Governs *how* every message is written; `knowledge/*` governs *what* it says.
- `anti_ai_writing_style.md` — banned words/patterns; the mandatory final gate on every message.

> The paid-media repo's marketing `tone_of_voice.md` was intentionally **not** carried over — that
> voice (challenger swagger, food/P&L wordplay, stacked headlines) reads as canned in a 1:1 cold email
> and kills trust. Brand *substance* (the POV) survives in `outbound_voice.md`; brand *packaging* does not.
