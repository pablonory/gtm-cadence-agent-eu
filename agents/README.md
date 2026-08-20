# Agents

Sub-agent definitions, grouped by pipeline stage. Each file defines one sub-agent: its role,
inputs, tools, and the structured output it returns.

## stage1_signals/ — SCORE (per account)
- `ga_leadership_hire.md` — new C-suite / ops / finance hire <90 days in role
- `ga_funding.md` — recent funding / investment
- `ga_open_jobs.md` — open ops / finance / IT roles
- `ga_new_location.md` — new site openings
- `ga_score_aggregator.md` — combines all signals → overall score, why-now, dedup + hot-account rules → HubSpot

Each signal agent returns: `{present, strength 1–5, recency_days, evidence, source_url, confidence}`
and reads its research method from `directives/signals/<signal>.md`.

## stage2_knowledge/ — KNOW (built once, refreshed)
Positioning (2a):
- `ga_product_knowledge.md`
- `ga_benefits_pmm.md`
- `ga_pains_benefits_vertical.md`
- `ga_jtbd_persona.md`

Field evidence from Gong (2b):
- `ga_gong_call_analyst.md` — winning vs losing talk tracks, objections + handling, per vertical×persona×stage
- `ga_gong_sequence_analyst.md` — reply/meeting rates by step, where sequences die (Gong REST API; needs a `gong_pull.py` extension for sequence data)
- `ga_win_loss_synthesizer.md` — correlates patterns with deal outcomes (Gong × HubSpot)

## stage3_cadence/ — CADENCE
- `ga_cadence_designer.md` — Output A: **maps** each account to the matching Gong **UKI flow** (`cadences/UKI_FLOWS.md`, pending confirmation) — does not design cadences
- `ga_first_touch_email.md` — Output B: the one bespoke first-touch email
- `ga_linkedin.md` / `ga_call_script.md` — templated channel steps
- `ga_account_pdf.md` — assembles the per-account PDF into the rep's Drive folder

> Files are stubs until we fill them in (next build step).
