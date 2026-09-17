# Proof-point verification against published nory.ai pages — 2026-09-17

Verification of the case-study numbers in `william_hit_list_prompt.md` (and the
`proof_library.md` 2026-09-17 addendum) against the live success-story pages. Method: plain
HTTPS fetch of each page (all returned 200; no Firecrawl fallback needed), text extracted and
read in full, plus a sweep of the success-stories index, sitemap.xml, homepage and key
product/solution pages for the two unsourced email-copy claims.

## Summary table

| Brand | Claimed | Page states | Verdict | URL |
|---|---|---|---|---|
| Black Sheep Coffee | 73 → 130+ sites, 98% forecast accuracy, <1% labour cost variance | Grown "from 73 sites at the start of 2024 to more than 130 locations across the UK and US"; "forecast accuracy is currently running at 98%"; "labour cost variance of under 1% of sales during Q1 2026" | CONFIRMED | https://www.nory.ai/success-stories/black-sheep-coffee-scaling-operations-with-nory |
| Pieminister | Reporting time −50%, food waste −60%, consolidated 10+ systems | "Reduced the time we spend on month-end and reporting by around 50%"; waste "an approximate 60% reduction… from the original benchmark" (stat block says "up to 60%"); "more than 10 systems" consolidated, incl. Access Group | CONFIRMED (note "up to"/"around" qualifiers) | https://www.nory.ai/success-stories/pieminister-builds-financial-clarity-and-operational-confidence-with-nory |
| Digbeth Dining Club | 0.38% labour accuracy, 70–71% GP | "Labour now lands within 0.38% of plan" ("variance between planned and actual labour cost 0.38%"); "GP holds at 70–71%" (stat block "~70–71%") | CONFIRMED | https://www.nory.ai/success-stories/inside-digbeth-dining-clubs-system-for-labour-accuracy-and-strong-gp |
| Papa's Fish & Chips | Cost control at scale without price rises (qualitative) | Qualitative story confirmed; **no quantified outcome figure anywhere on the page** (only "5 locations", "third-generation") | CONFIRMED (qualitative only) | https://www.nory.ai/success-stories/how-papas-fish-chips-controls-costs-as-they-scale |
| Tasty African Food | 22 → 29 locations, margin control | Stat block "22 → 29 locations in 2 years (with Nory)"; margin/variance control is the whole story. Bonus figures: 98.5% forecast accuracy, 75% food waste reduction, 70+ SKUs | CONFIRMED | https://www.nory.ai/success-stories/tasty-african-food-controls-margins-across-locations-with-nory |
| Hampshire Pub Co | Payroll admin 2 days → under 1 hour, labour admin −50% | "What used to take me nearly two full days now takes less than an hour" (stat "< 1 hour… ~2 days previously"); "labour-related admin time has been reduced by 50%" (stat "~50%") | CONFIRMED | https://www.nory.ai/success-stories/hampshire-pub-co-builds-the-infrastructure-to-scale-with-nory |
| Barge East | Labour costs −10% via forecasting | "Reduced labour costs by up to 10%"; quote: "It's helped us cut labour costs by 10% in some areas"; forecasting (weather-based) is the stated mechanism | CONFIRMED (quote as "up to 10%") | https://www.nory.ai/success-stories/barge-east-cuts-labour-costs-with-nory |
| Pizzarova | 1 → 5 sites, reduced labour costs | 5 locations (2 openings pending); origin is a Land Rover pizza oven at Glastonbury 2013 — index blurb: "from a single Land Rover oven to a thriving five-site restaurant brand". Stat block "Reduction in labour costs 10%"; body says "improving labour efficiency by around 10%" | CONFIRMED | https://www.nory.ai/success-stories/pizzarova-builds-scalable-restaurant-model-with-nory |
| Roasting Plant Coffee | Labour −18% in 2 months | Page exists. "Reducing cost of labour by 18% in just two months"; stat block "Cost of Labour −18%", "Sales forecast accuracy 98%" (within 2.8%); 15 locations UK & US | CONFIRMED | https://www.nory.ai/success-stories/roasting-plant-takes-control-of-labour-with-nory |
| Josie's | Labour −23% in 4 months | Page exists. "Reducing cost of labour by 23% in just four months"; stat block "Cost of labour (in the first 4 months) −23%", "+20.5% Sales / labour hour"; 5 locations | CONFIRMED | https://www.nory.ai/success-stories/josies-cafe-success-story |
| Rocksalt | COL −7%, 97.5% forecast accuracy | Page exists. "Reduce labour costs by 7%"; "forecasting sales to with[in] 97.5% accuracy"; 5 venues + 2 CPUs, Ireland | CONFIRMED | https://www.nory.ai/success-stories/rocksalt-reduces-labour-costs-and-grows-business-with-nory |
| Griolladh | Food truck → 3x franchise | Page exists. "Griolladh grows business size x3 with Nory"; started with "a trailer" in June 2020, now a franchise. Header says 6 locations, body says "five locations" (internal inconsistency) | CONFIRMED (say "trailer", not "food truck"; avoid a site count) | https://www.nory.ai/success-stories/griolladh-launches-successful-restaurant-franchise-with-nory |
| Rep email copy | "6–11% reductions in labour" | Not on any page checked. Nearest published: **5–11%** "Labour savings for pilot sites" (Scheduling Assistant page) and "COL savings with Scheduling Assistant 5–11%" (Workforce page). Other published ranges: 10–25% (Product page and Workforce FAQ), "up to 20%" (Agentic AI page) | UNSOURCED (likely a misquote of 5–11%) | checked: /, /product, /product/workforce-management, /agentic-ai, /agentic-ai/scheduling-assistant, /roi-calculator, success-stories index |
| Rep email copy | "a 6% uplift of their GP" | Not on any page checked. Nearest published GP figure: Hook & Ladder "Improvement in GP 4%" (card on /product) | UNSOURCED | same sweep as above |

## Notes

- **Every URL in William's table resolves (200) and every published number he cited checks
  out.** The four brands he listed without URLs (Roasting Plant, Josie's, Rocksalt, Griolladh)
  all have live pages, found via sitemap.xml — they are simply not surfaced on the first page
  of the success-stories index (the index paginates behind a "Load more" button).
- **Black Sheep**: the page attributes the figures to the customer ("According to Black Sheep
  Coffee…"), and the <1% labour variance is time-boxed to Q1 2026. Also quotable: demand
  forecasting in 15-minute intervals across sites. Quote from Ula Spire, Head of Operations.
- **Pieminister**: the stat block hedges both headline numbers with "up to". The waste figure's
  mechanics: long-standing 1% waste target, now consistently 0.2–0.4% in normal trading weeks
  — that is where "approximate 60% reduction" comes from. Copy should say "around 50%" /
  "up to 60%", not bare "−50%/−60%".
- **Digbeth**: "0.38% labour accuracy" is shorthand; the page's precise framing is "variance
  between planned and actual labour cost" / "labour lands within 0.38% of plan". Labour cost
  itself runs 15–22% depending on venue model. Use the variance framing in copy.
- **Papa's**: genuinely no outcome numbers — the story is qualitative (visibility, precision
  deployment, facts-based decisions, no portion cuts or price rises). Do not attach a figure.
- **Tasty African Food**: the page gives more than the claim — 98.5% forecast accuracy, 75%
  food waste reduction, 70+ SKUs, 14 equity + 15 franchise stores, CEO target of 100 sites in
  five years. A second Tasty page exists (change management).
- **Barge East**: the body text says "up to 10%" and the founder quote says "10% in some
  areas"; only the stat block strips the qualifier. Safer copy: "cut labour costs by up to 10%".
  Secondary: managers save 4–5 hours/week.
- **Pizzarova**: "1 → 5" is a fair gloss (single Land Rover oven → 5 sites, per the index
  blurb) but the page itself never writes "1 → 5". The labour number is 10%, phrased as
  "improving labour efficiency by around 10%" in the body.
- **Griolladh**: the page contradicts itself on site count (header "6", body "five"); the safe
  quotable is the x3 growth and the trailer-to-franchise arc. It began with a trailer, not
  strictly a food truck.
- **The two unsourced email claims**: "6–11%" appears nowhere; the published Scheduling
  Assistant range is **5–11%** (pilot sites), so William's templated emails either misquote it
  or use an internal number. No page states a 6% GP uplift; the only published GP improvement
  figure is Hook & Ladder's 4%. Both claims should not be used in agent copy until William
  points to a source; suggest correcting to the published 5–11% and dropping or re-sourcing
  the GP line.
- Extra proof points surfaced during the sweep (candidates for `proof_library.md`, all
  published): Passyunk Avenue COL −26% (95 employees), Hook & Ladder GP +4%, CUPP food waste
  −60% / 99% forecast accuracy, Badiani 96% forecast / operating costs −3%, Masa forecasting
  story, plus platform-level claims "10–25% reduction in cost of labour" and "up to 50%
  food-waste reduction" (/product).
