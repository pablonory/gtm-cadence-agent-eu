# Gong evidence pack — Coffee/Café × Finance

> ⚠️ **TEMPLATE / AWAITING DATA.** This is the schema for a Stage 2b evidence pack. It is **empty on
> purpose** — the content must come from **real Gong calls**, never invented. Populate it via:
> - **PRIMARY:** the **Gong REST API** — run `scripts/gong_pull.py` (`GONG_ACCESS_KEY`/`GONG_SECRET` in
>   gitignored env) to pull calls + verbatim transcripts into `output/gong/`, then the Stage-2b agents read them.
> - Supermetrics Gong connector is **gated behind early access** — not available.
>
> Produced by `ga_gong_call_analyst` + `ga_gong_sequence_analyst` + `ga_win_loss_synthesizer`.
> One pack per matrix cell. Every line in a live pack must cite the call/deal it came from.

## Cell
Vertical **Coffee** × Persona **Finance**. Matches cadence `cadences/coffee_cafe_finance.md`.

## 1. Top objections + handling that overcomes them
> Start from the shared library `_objections.md` (the 5 cross-cutting objections + handling). Add here
> only what's **specific to Coffee × Finance** (e.g. objections/incumbents unique to this cell).

| Cell-specific objection | How winning reps handle it | Source (call ID / deal) |
|---|---|---|
| _from Gong_ | _from Gong_ | _cite_ |

## 2. Voice-of-customer language (verbatim once Gong API is wired)
> The exact words coffee finance leads use for the pain. Feeds first-touch phrasing so it sounds like
> the buyer, not like us. **Verbatim only from transcripts — no paraphrase presented as a quote.**
- _from Gong_

## 3. Winning proof points (what actually moved this cell's deals)
| Proof used | Won/advanced? | Source |
|---|---|---|
| _from Gong × HubSpot outcome_ | | |

## 4. Behavioural signature of calls that advance
> Talk ratio, # questions, customer-story length, etc. — the shape of a call that converts in this
> cell. From call analytics.
- _from Gong analytics_

## 5. Sequence intel (which steps convert / die)
| Step | Reply / meeting rate | Notes |
|---|---|---|
| _from Gong sequence/flow data (needs gong_pull.py extension)_ | | |

---
## Status
- [ ] Gong API creds set (`GONG_ACCESS_KEY`/`GONG_SECRET`) + `scripts/gong_pull.py --transcripts` run
- [ ] Calls + transcripts pulled and bucketed for Coffee/Café × Finance
- [ ] Outcome join done (Gong call behaviour × HubSpot deal stage on account/opportunity_id)
- [ ] Sequence/flow stats (needs a `gong_pull.py` extension for cadence analytics)

> Until this pack has real data, `cadences/coffee_cafe_finance.md` copy is grounded only in positioning
> (`knowledge/*`), NOT field evidence. Flag that limitation on any deliverable that leans on it.
