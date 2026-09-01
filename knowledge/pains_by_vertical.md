# Pains by vertical ↔ the Nory benefit that answers each

> Stage 2a knowledge. Per vertical: the operational pains and the Nory benefit + proof that answers
> them. **This is the default first-touch angle** before a Stage-1 signal sharpens it.
>
> **Maintenance rules** (folded in 2026-08-24 from the deleted `ga_pains_benefits_vertical.md`):
> - Ground pains in the vertical definition + real hospitality economics, **not stereotype**.
> - Match proof to the vertical's reference brands — never quote a coffee win to an FSR account.
> - When Gong evidence exists, replace assumed pains with the ones customers actually voice.
>
> *(The old rule "Casual stays borrowed from QSR/FSR until Lewis confirms" is dropped — Lewis confirmed
> on 2026-08-10 and Fast Casual is now its own vertical. See its section below.)*

## Coffee / Café (multi-site coffee groups, all-day cafés, bakeries — merged v1)
| Pain | Nory answer | Proof |
|---|---|---|
| Labour % swings on unpredictable AM/daypart peaks | schedule to 15-min forecast demand | −10–20% labour |
| Milk/bean/fresh COGS + waste per site | order to forecast, live COGS | −~50% waste |
| Perishable/prep spoilage eroding thin margins | inventory vs forecast | waste down, GP up |
| Every new site multiplies the margin blind spot | live P&L per site | catch drift weekly |
> **Default angle:** can't see labour % / COGS by site until month-end — by then the leak's banked.
> ⚠️ **Proof-light vertical** — no hard coffee outcome number yet; lean on forecasting-accuracy, the
> £25k-milk COGS stat (if pain = GP), or the US coffee logo cluster (`proof_library.md`), never a fabricated %.

## QSR (quick-service, often franchised)
| Pain | Nory answer | Proof |
|---|---|---|
| Throughput-driven labour scheduling | optimal schedules in seconds | −10–20% labour |
| Portion/variance control across many sites | variance control + live P&L | DHC 0.5–1% weekly variance |
| Franchise consistency / margin discipline at scale | one OS, standardised across sites | DHC +19.4% GP |
> **Default angle:** scaling sites without a system means variance creeps and margin discipline slips.
> **VOC anchor (QSR C-suite):** *"We've almost given up trying to control labor. It's so high."* — MD,
> QSR (`gong_evidence/_voc.md`). QSR leadership is often already resigned to the labour number, not
> unaware of it. Open on the resignation, not the feature.
> ⚠️ Qualify POS fit before spending the cadence — QSR carries the most DQs (`context/icp/verticals.md`).

## Full-service (FSR — sit-down, served)
| Pain | Nory answer | Proof |
|---|---|---|
| Complex rota + compliance across large teams | scheduling with compliance built in | 12.3 hrs saved/day (250-site) |
| Larger menu COGS to control | forecast-driven ordering + live COGS | operating costs −up to 20% |
| Front+back-of-house labour balance | optimal schedules against demand | 96% GMs rate schedules good/great |
> **Default angle:** big teams + big menus = the most moving parts; margin leaks hide in the complexity.
> Highest-ACV vertical, longest cycle, most stakeholders (`context/icp/verticals.md`).

## Fast Casual ⚠️ no pain set yet
**Its own vertical since 2026-08-10** (`context/icp/verticals.md`) — it is no longer folded into QSR, and
the earlier "Casual (pending), borrow QSR or FSR" rule that lived here is **reversed and removed**.

But it has **no pain table of its own**, and no pipeline or conversion data behind it — the vertical was
carved out to match Lewis's Gong flow structure, not off evidence. Until there is real Fast Casual
evidence: borrow by service model (counter-order → QSR pains; elevated/fresh-prep with table service →
FSR pains) and **say in the brief which one you borrowed**. Do not present a borrowed pain as
Fast-Casual-specific, and do not invent one.

## How this is used
Three tiers, most specific wins (see `knowledge/conjunctural/README.md`):
1. **Account signal** (Stage 1) — sharpens the default angle into something specific to them
   (e.g. Coffee default → "3 new sites + new COO"). Always wins when present.
2. **Conjunctural signal** (Stage 2, `knowledge/conjunctural/`) — for accounts with no account signal
   or a score under the threshold (`CONJUNCTURAL_THRESHOLD` in `score_accounts.py`): a dated
   industry/macro fact (wage step, tip-credit change, commodity move…) quantified against *their*
   state/vertical/footprint via `scripts/conjunctural_match.py`. Only used when quantifiable — an
   unquantified macro cliché is worse than this fallback.
3. **This file's default angle** — the true-but-generic vertical pain, used when neither of the above
   applies. The floor everyone lands on eventually.
