# Pains by vertical ↔ the Nory benefit that answers each

> Stage 2a output, produced by `ga_pains_benefits_vertical`. For each vertical, the operational pains
> and the Nory benefit + proof that answers them. Feeds the cadence angle per cell. Seeded v1 —
> refreshed on each Stage 2 run (and sharpened by Gong evidence when available).

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

## QSR (quick-service / fast-casual, often franchised)
| Pain | Nory answer | Proof |
|---|---|---|
| Throughput-driven labour scheduling | optimal schedules in seconds | −10–20% labour |
| Portion/variance control across many sites | variance control + live P&L | DHC 0.5–1% weekly variance |
| Franchise consistency / margin discipline at scale | one OS, standardised across sites | DHC +19.4% GP |
> **Default angle:** scaling sites without a system means variance creeps and margin discipline slips.

## Full-service (FSR — sit-down, served)
| Pain | Nory answer | Proof |
|---|---|---|
| Complex rota + compliance across large teams | scheduling with compliance built in | 12.3 hrs saved/day (250-site) |
| Larger menu COGS to control | forecast-driven ordering + live COGS | operating costs −up to 20% |
| Front+back-of-house labour balance | optimal schedules against demand | 96% GMs rate schedules good/great |
> **Default angle:** big teams + big menus = the most moving parts; margin leaks hide in the complexity.

## Casual (pending — see `context/icp/verticals.md`)
Not a confirmed cell. Until Lewis confirms, borrow QSR (counter) or FSR (table-service) pains by the
account's service model.

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
