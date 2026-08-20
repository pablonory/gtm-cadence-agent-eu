# Knowledge base (Stage 2 output)

The agent's shared "brain" — built once and **refreshed periodically**, not re-run per account.
Read by Stage 3 when writing cadences and first-touch emails.

## Positioning (2a)
- `product.md` — what Nory does (from `context/product/`)
- `benefits.md` — features → benefits → proof points
- `pains_by_vertical.md` — operational pains per vertical ↔ the Nory benefit that answers each
- `jtbd_by_persona.md` — jobs-to-be-done per persona (Ops / Finance / C-suite)

## Field evidence (2b) — `gong_evidence/`
- `_objections.md` — **shared** objection library (cross-cutting, applies to every cell). Populated.
- `_voc.md` — **shared** voice-of-customer verbatim pain language, by persona. Populated.
- `_sequence_performance.md` — **shared** sequence/channel intel + the reply/meeting-rate data gap
  (no centralized rates yet), the US podcast sequence, and the 8%→39% multithread stat. Populated.
- `_signal_correlation.md` — **shared** signal ↔ closed-won ranking (LOW confidence) + the contract-
  expiry compelling event + the funding-signal caveat. Feeds scoring weights. Populated.

Plus `proof_library.md` (in `knowledge/`) — named-brand case-study proof by vertical; the
merge-field source for cadence copy. Populated (coffee is the known gap).
- One evidence pack per matrix cell (e.g. `fsr_finance.md`, `coffee_cafe_finance.md`), from real Gong calls:
- Top objections + the handling that overcomes them
- VOC language reps actually hear (verbatim, from Gong REST API transcripts via `scripts/gong_pull.py`)
- Winning proof points and the behavioural signature of calls that advance (talk ratio, questions, customer-story length)
- Which sequence steps convert / die

> "What's working" is defined by **outcome correlation**: join Gong call behaviour/recaps with
> HubSpot deal stage/outcome on `opportunity_id` / account — Gong via the REST API pull, deals via HubSpot MCP.
