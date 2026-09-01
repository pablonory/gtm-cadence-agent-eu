# Gong evidence pack — Full-service (FSR) × Finance

> Field-evidence pack for the **FSR × Finance** flow. Draws on the shared files
> plus FSR-specific proof. Cell-specific call data still to come from Gong (see status).

## Cell
Vertical **Full-service (FSR)** × Persona **Finance** (casual dining classified as FSR).

## 1. Objections + handling
Use the shared `_objections.md` (all 5). Most relevant to this cell:
- **#3 Unclear ROI (finance):** the **Labour Assessment** — model the £/$ saving up front ("~£40k labour +
  ~£11k GP variance" format). Finance wants a number, not "save time".
- **#2 Incumbent:** get the contract end date on call 1; if on **XtraChef/inventory-first**, use the
  US displacement story (`proof_library.md`).

## 2. Voice-of-customer (from `_voc.md`, Finance)
- *"The inaccuracies were affecting the P&L and our overview for Q1 and Q2. We just want accurate GP,
  accurate stocks, accurate labour."*
- *"There's a difference of one or two percent, so I always get 'which one is right?'"*
> Lead the first touch / opener on the **"which number is right?"** accuracy pain.

## 3. Proof (from `proof_library.md`, FSR — the strongest set). **These are real UK/EU results.**
- **Passyunk Avenue — COL −26%** (strongest published labour number).
- **Grounded Kitchen — COL −4.8% (£50k/yr UK); GP +1.2% (£65k); waste −24%/qtr.**
- **Jamie Oliver Group — COL −9% over 6 months (£56,676/yr, IE); forecasting within 4%.**
- **Masa — COL −9.7% (€81,480/yr).**
> **US rule:** lead with the **%** (currency-neutral); model any $ figure on the prospect's own cost base
> (Labour Assessment). The £/€ absolutes are UK/EU actuals — **never relabel as $**.

## 4. Behavioural signature of calls that advance
_from Gong — pending (see status)._

## 5. Sequence intel
No centralized rate data yet (`_sequence_performance.md`). FSR = longer cycle (~18–22d, 45–55 for
pilots) → the full multi-threaded cadence fits; multithread ≥3 (Ops opens → Finance validates → Owner
decides).

---
## Status
- [x] Objections / VOC / proof seeded from shared evidence + `proof_library.md`
- [ ] FSR×Finance calls + transcripts pulled via `scripts/gong_pull.py` (Gong REST API — needs creds)
- [ ] Sequence/flow stats (needs a `gong_pull.py` extension for cadence analytics)
- [ ] Outcome join (Gong behaviour × HubSpot deal stage)

> This cell is **evidence-backed on proof + VOC + objections**, but call-behaviour/sequence specifics are
> still positioning-level until Gong data is wired. Flag that on deliverables.
