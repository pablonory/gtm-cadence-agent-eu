# Verticals — the cadence matrix (rows)

> One of two axes of the Stage 3 matrix (the other is `personas.md`). The **Vertical** column in the
> accounts sheet picks which of these a rep's account belongs to, and therefore which Stage 3 cadence
> template cell applies. Grounded in Nory's named-brand base (see `context/product/product.md`) and
> standard hospitality segmentation.

> **UKI fork note (2026-08-20):** the vertical set below is the **inherited US matrix** — the UKI
> Gong flows are unconfirmed (`cadences/UKI_FLOWS.md`), and the **pubs & bars question is open** (a
> major UK segment with no US cell; gastropubs currently classify FSR). The reference brands are
> largely UKI already (Black Sheep, Grind, Bewley's, Camile Thai, Sticks'n'Sushi…). The "US pipeline
> distribution" table further down is US-fork evidence — a UKI pipeline read is TBD.

## The four verticals (inherited candidate — pending UKI flow confirmation)

| Vertical | Definition | Nory reference brands | What makes their prime cost bleed |
|---|---|---|---|
| **Coffee / Café** | Multi-site coffee groups, speciality coffee, all-day cafés, bakeries, brunch-led. High-frequency, low/mid ticket, tight labour ratios, heavy AM peak + perishable prep. *(Merged: US pipeline treats coffee + café/bakery as one behaviour.)* | Black Sheep Coffee, Grind, Roasting Plant, Bewley's, Boston Tea Party, Badiani, Oakberry | Labour % on unpredictable peaks; milk/bean/fresh COGS + waste; daypart swings; each new site multiplies the blind spot |
| **QSR** | Quick-service, counter-order, high throughput, drive-thru, often franchised. | Dave's Hot Chicken (Azzurri), CUPP, Mad Egg | Throughput-driven labour scheduling; portion/variance control across many sites; franchise consistency |
| **Fast Casual** | Counter-order but elevated / fresh-prep, higher ticket than QSR, limited (or no) table service. **Its own vertical as of 2026-08-10** — no longer folded into QSR or FSR. | (US fast-casual chains) | Fresh-prep COGS + waste; peak-throughput labour; menu variance across sites |
| **Full-service (FSR)** | Sit-down, served, higher ticket, larger/complex menu and teams. Genuinely full-service sit-down only — counter-service casual → Fast Casual. | PF Chang's, Camile Thai, Sticks'n'Sushi | Complex rota + compliance; larger menu COGS; front+back-of-house labour balance |

## UPDATED — Fast Casual IS its own vertical (2026-08-10)
Reverses the 2026-07-17 "casual → FSR" call (US-fork history: Lewis built a separate Fast Casual flow
set in the US Gong flows, and Gong is the source of truth): counter-service / fresh-prep fast-casual is its
own vertical with its own cadence cells, no longer folded into QSR or FSR. Genuinely full-service sit-down
groups stay **FSR**; multi-concept groups remain a separate motion, not a cell.
> The segment × persona sub-distinction still holds *within* each vertical: multi-unit groups (5–15 sites,
> COO + Finance in the room) convert faster / higher-ACV than owner-operator (1–3 sites, where the
> **Founder** is the buyer → Founder flow). Handle via segment band + persona, not a further vertical split.

## US pipeline distribution + conversion (sales-intel app, 2026-07-17)
From the 100-deal US pipeline. Use for **prioritisation**, not as measured win rates (small samples).

| Vertical | Pipeline vol | Active open | US wins | Verdict |
|---|---|---|---|---|
| **Coffee / Café** | ~12 | 4 | **4** | **Best conversion — lead with the cluster** |
| **QSR / Fast-casual** | ~35 | 5+ | 6 | Widest funnel, most DQs (NRA-2026 prospecting) — **be selective / qualify hard** |
| **Full-service / Casual** | ~20 | 8 | 2 (Pilots: Ark, Heirloom) | **Highest ACV**, longer cycle, more stakeholders — worth the full multi-thread |
| **Multi-concept / hospitality groups** | ~10 | 2 | **0** | Low conversion (too large/complex, wrong buyer) — **deprioritise; not a cadence cell** |

- **Multi-concept groups** (Lettuce Entertain You, Gordon Ramsay £100k open, MTY, RBI…) show up in the
  pipeline but **haven't converted** — treat as a watch-list, not a v1 cadence target.
- **QSR** carries the most disqualifications (incl. POS-integration DQs) — qualify POS fit + buyer before
  starting a cadence.

## Coffee + Café merged (resolved 2026-07-17, Pablo)
Collapsed to a single **Coffee/Café** vertical for v1 — the US pipeline lumps them (the 12 includes
bakeries: Fortuna, Somedays, Boudin, West Coast Sourdough) and they behave alike. File prefix
`coffee_cafe_`. Split later only if evidence shows they diverge.

## How the vertical is used
- Sheet `Vertical` dropdown → **Coffee & Cafe / Fast Casual / FSR / QSR** (counter-service casual → Fast
  Casual; gastropubs → FSR pending the pubs & bars decision; multi-concept → classify by the group's
  dominant service style).
- Selects the Stage 3 template cell (`cadences/<vertical>_<persona>.md`).
- Drives the proof point pulled per send — always match the reference brand to the account's vertical
  (never quote a coffee win to a full-service prospect).
- Shapes the pain angle: the "what bleeds" column above is the default first-touch angle before
  signals sharpen it.

> **All verticals are equal-priority targets** — Coffee & Cafe, Fast Casual, FSR and QSR alike. Cadences
> are the Gong **UKI flows** (`cadences/UKI_FLOWS.md` — placeholder until confirmed). The per-cell
> brief files were removed 2026-09-01 (following the US repo's 2026-08-24 removal at cbb37d1); the
> first touch is built straight from `knowledge/` — see UKI_FLOWS.md.
