# Signal playbook — Recent funding / investment

> Versioned research method for the `ga_funding` sub-agent. Adapted from the BDR Clay signal doc
> (Tier 1). The learning loop rewrites this file as detection sharpens.

## What it detects
A **funding, investment, or acquisition** event at the target account within the last **12 months**
(widened from 6 on 2026-08-12 — see *Applied feedback*): equity raise (seed → growth), PE/VC investment,
debt facility for expansion, or being acquired by / acquiring another group.

## Why it matters for Nory
Fresh capital = an expansion mandate = new sites, new hires, and pressure to protect margin while
scaling. Investors want unit economics under control. This is a strong "why now" for prime-cost
control at portfolio scale — especially paired with a new-location or leadership signal.

## Where to look (UKI-first — flipped at fork 2026-08-20)
1. **News / press releases** — "raises", "secures", "closes <£/€>", "backed by", "investment".
   Search: `"<Company>" (raises OR funding OR investment OR acquired OR "private equity") restaurant`.
2. **Companies House filings — the primary-source corroboration** (was "the UK analogue" in the US
   fork; here it's the main event): **SH01 share allotments**, confirmation statements showing new
   shareholders, charges registered (debt facilities), and PSC changes (ownership/control moves —
   the PE-exit signal). Free API + web. Ireland: CRO filings.
3. **UK/IE deal press** — **Propel** (daily transactions wire), MCA Insight, Big Hospitality,
   The Caterer; **Sifted / UKTN** for venture-side raises; PE Hub Europe / Unquote for PE moves;
   The Times/Sky News city desks break UK hospitality M&A early.
4. **Crunchbase (public pages)** — round/date/investor corroboration.
5. **HubSpot** — existing enrichment / notes on the account.
6. *(US accounts only)* SEC EDGAR Form D, US Business Journals, Restaurant Finance Monitor.

## How to verify
- Confirm the event is about the **target account** (not a namesake or a supplier).
- Capture **amount + round + investor + date** where available.
- Distinguish an **expansion/growth** raise (high relevance) from a distressed/rescue raise (note it —
  different angle).
- Prefer a named source URL; a single reputable outlet is enough for `confidence: med`.
- **Capital withdrawn is not capital raised.** Check the direction of the money before scoring: a grant
  awarded to a *city*, a project the group walked away from, an "exploring investors" quote, or an
  open solicitation for expansion partners are all `present:false`.

## Scoring rubric
> **Recency is a discount, not a gate** (2026-08-12). Score `strength` on the *substance* of the deal and
> put the age in `recency_days` — `score_accounts.py` applies the decay (≤90d ×1.0 · ≤180d ×0.8 ·
> ≤270d ×0.6 · ≤365d ×0.4 · beyond 365d not counted). Do **not** also down-rate `strength` for age, or
> the discount is applied twice.

| Field | Rule |
|---|---|
| `present` | true if a funding/investment/M&A event within **365 days** |
| `strength` (1–5) | Substance only, ignore age: 5 = growth/expansion raise with a stated site or scaling plan · 4 = growth raise or PE/majority stake, no stated plan · 3 = debt facility / minority investment / acquisition of the group · 2 = small or undisclosed amount · 1 = rumoured only |
| `recency_days` | days since announcement — **`null` if no source publishes a date** (see below) |
| `confidence` | high = named outlet + a filing (Companies House SH01/PSC · IE CRO · SEC Form D for US accounts) or second outlet · med = one named outlet · low = rumour/aggregator only |

### Undated but corroborated
Common in this segment. If the event is real and sourced but **no source gives a date**, set
`present: true`, `recency_days: null`, and cap `confidence` at `med`. The scorer applies a ×0.85 haircut.
Do **not** score it `present:false` — that throws away real intel and was the single biggest recall leak
in the first 80 accounts. Say so in `evidence`: *"no publishable date found"*.

### Out of window
A real deal older than 365 days is **`present:false`** for scoring, but still belongs in the brief as
context — put it in the `note` and let `why_now` reference it (e.g. *"PE-backed since Sept 2025, still
expanding"*). A stale raise can explain a WARM read even when it scores nothing.

## Output
`{present, strength, recency_days, evidence, source_url, confidence, amount, round, investor, hook_detail}`
- `hook_detail` = **the first-touch hook material**: the stated *purpose* of the raise beats the amount
  (e.g. `"$12M Series A 'to reach 25 locations by 2028'"` — the expansion quote is the hook). Verbatim-
  checkable from the source; empty if only the bare round is known.

## Dedup / suppression
**Primary = baseline diff** (`directives/signals/_delta_state.md`): only a round newer than stored
`funding.date` counts. 14-day suppression is a fallback. Don't double-count one round across outlets.

## Source & access (v1)
Agent-first: WebSearch/WebFetch of press + funding databases. Reachable and cheap — **no augment needed**
(and funding scored LOW deal-correlation, so don't invest in tooling here). See `directives/signals/_signal_stack.md`.

## Applied feedback
- [2026-07-17] correction — **funding has zero support in Nory's closed-won deal data** (was Tier-1 in
  the BDR Clay outbound doc). Down-weighted to **low** in scoring, flagged unvalidated. Keep hunting it,
  but don't over-index the score on it until deal data confirms. (source: sales-intel app, see
  `knowledge/gong_evidence/_signal_correlation.md`)
- [2026-08-12] **window widened 180 → 365 days; recency became a discount, not a gate.** Measured on the
  first 80 real accounts (batch 2 + reactivation batch 1/6): funding fired **0 times out of 80**. The
  cause was not an absence of deals — agents found several and correctly refused to score them, because
  each fell just outside the old 180-day gate or carried no publishable date: Sicilian Oven's Goode
  Partners PE at **252 days**, The h.wood Group's DIAFA majority stake at **324 days**, Insomnia Cookies'
  Verlinvest/Mistral buyout at **~14 months**. Under the new model the first two now score (×0.6 and ×0.4)
  and the third stays out, which is the right answer for all three.
- [2026-08-12] **anti-fabrication holds — don't loosen it.** In the same 80 accounts the agents rejected a
  hallucinated "$50M Series H" (search contamination from an unrelated company), an unsourced "acquired by
  C3 Capital" claim contradicted by every other source, an undated $10M raise, and a Tracxn snippet whose
  source page 404'd. The 0/80 was partly a *quality* result. Widening the window must not become licence
  to count unverifiable rounds — `confidence: low` still caps the account at 59.
- [2026-08-20] **UKI fork** — Companies House SH01/PSC filings promoted from 'UK analogue' to the
  primary corroboration source; Propel/MCA lead the press list. Window/decay/anti-fabrication rules
  carried over; the 0/80 recall history and its fixes are US-fork evidence.
