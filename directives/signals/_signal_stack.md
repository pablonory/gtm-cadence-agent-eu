# Signal stack — how Stage 1 detects signals (architecture + v1 decision)

> **UKI fork note (2026-08-20):** all measured-recall numbers in this file (the 80-account table,
> the ATS/403 failure counts) are **US-fork data**, kept as the engineering evidence behind the
> mechanics (delta layer, recency-as-discount, jobs probe, permits-first). The mechanics carry over;
> the UKI source lists live in the per-signal playbooks. Re-measure recall on the first UKI batches
> before tuning anything.

> Design note for the Stage 1 signal system; companion to the per-signal playbooks and
> `knowledge/gong_evidence/_signal_correlation.md` (which signals actually correlate with wins).
> Decisions set with Pablo, 2026-07-17.

## Principles
1. **Signals are deltas, not lookups.** Detect *change* against stored account state — "new site" =
   today's locations − last run's; "new hire" = an exec not present last run. **This is the backbone —
   more important than any scraper — and it's now built: see `directives/signals/_delta_state.md`**
   (schema, run cycle, per-signal delta rules, first-run + freshness). State lives in a gitignored
   per-account snapshot (`output/state/<domain>.json`); HubSpot holds the human-facing outputs.
2. **Match the access method to each signal** — not one tool for all four.
3. **Agent-first, then augment.** At low volume (Lewis's US AE team), Claude agents + WebSearch/WebFetch
   are the default detector. Buy tooling only where *measured* recall is weak.
4. **Freshness + confidence on every signal** (`recency_days`, `confidence`) — signals decay.

## Layers
- **L0 — HubSpot state + delta:** system of record; prior locations/execs/contract dates; dedup + the
  baseline every delta is measured against.
- **L1 — Claude signal agents + WebSearch/WebFetch, now + Firecrawl:** the v1 detector for all four
  signals. **Added 2026-08-14** (premium plan): reach for
  `firecrawl scrape`/`crawl`/`map`/`search` (CLI, or the `firecrawl` MCP tools once available) when
  WebFetch/WebSearch hit the access failures below — JS-rendered pages with no crawlable HTML, and sites
  that flat-out block WebFetch (403/Cloudflare). It is still a fetch tool, not a structured-data source —
  doesn't change what counts as a verified signal, just what agents can actually reach. See
  `CLAUDE.md`'s integrations table.
- **L2 — structured augments (per measured recall gap):**
  - Jobs → ✅ **BUILT 2026-08-12: `scripts/jobs_probe.py`.** T1 = the company's own **ATS public JSON API**
    (free, dated, company-scoped — Greenhouse/Lever/Ashby/Workable/Recruitee/SmartRecruiters/Personio/
    Teamtailor); T2 = **Apify** scoped to a board URL (`APIFY_TOKEN` in gitignored env, REST not MCP) for
    boards with no public API (Workday/iCIMS/Paycor/Paylocity/ADP/Poached). See the measured-recall
    section below for why the careers page and aggregator search both failed as primary sources.
  - Locations → store-locator diff (agent, no scraper); Apify can scrape awkward locators if needed.
  - Leadership hire → **a compliant people / job-change data API** (LinkedIn is login-walled; agents
    can't reach it — this is the weakest signal). **No raw LinkedIn scraping (ToS/legal).**
- **L3 — verify / recency / confidence agent** (already in the playbooks).

## Access method per signal (v1)
| Signal | Agent reachability | v1 method | Later augment (only if recall is weak) |
|---|---|---|---|
| **new_location** | good | **permits/licences first** (dated, months early), then WebFetch store-locator + **diff vs stored state**; trade press | — |
| **open_jobs** | fixed by L2 | **`scripts/jobs_probe.py` first** — the company's own ATS via its public JSON API; the careers page is NOT the primary source (403/JS) | Apify T2, `--apify`, for boards with no public API |
| **funding** | good | WebSearch/WebFetch press | — (LOW deal-correlation — don't invest) |
| **leadership_hire** | **poor** (LinkedIn walled) | WebSearch trade press + company announcements | **people / job-change API** (the one worth paying for) |
| **contract_expiry** (CE) | n/a — not researched | read from HubSpot; probe on call 1 | — |

## Output contract — what every signal hunter returns
Consolidated here 2026-08-24 (US repo, ported at fork-sync 2026-09-01 from cbb37d1) from four deleted
prose wrappers that restated their own playbook and had drifted from it. **The playbook in this
directory is the method; this is the shape.** One rule, one place (`self_improvement.md`).

Every signal returns these seven fields, always — including on a miss, so the aggregator can log it:

```json
{"signal":"<name>", "present":true, "strength":1-5, "recency_days":47,
 "evidence":"one line, what and where", "source_url":"...", "confidence":"high|med|low",
 "hook_detail":"the specific source-checkable fact the first touch can use"}
```

`present:false` with a short `evidence` note — **never omit the field**. Plus per signal:

| Signal | Extra fields | Window (from the playbook, not the old wrappers) |
|---|---|---|
| `new_location` | `new_sites_count`, `total_locations`, `locations[]`, **`stage`** (`permit_filed`\|`announced`\|`fit_out`\|`opened`) | 365d |
| `leadership_hire` | `person_name`, `role` | 180d — widened from 90 on 2026-08-12 |
| `open_jobs` | `roles[]` of `{title, location, posted}` | none — current-state signal |
| `funding` | `amount`, `round`, `investor` | 365d — widened from 6 months on 2026-08-12 |

Always return `total_locations` when known — it feeds segment banding (`context/icp/segments.md`).

**Three defects the old wrappers carried, fixed in the table above.** They stated `<90 days` for
leadership hire and `~6 months` for funding and new_location, all superseded on 2026-08-12; and
`ga_new_location.md` omitted **`stage`** entirely although `new_location.md` marks it required and
promoted licences to check #1. A fourth is *not* fixed because it cannot be: all four wrappers cited a
**"14-day suppression"** as a fallback, and that rule **is not defined anywhere in this repo**. Do not
cite it. The baseline diff in `_delta_state.md` is the mechanism.

> **No writes from a signal hunter.** Scoring and the single write are the aggregator's job
> (`hubspot-app/scripts/score_accounts.py` → `upsert_brief.py`), and everything lands on
> `cadence_brief`, never on a COMPANY property.

## MEASURED RECALL — first 80 real accounts (2026-08-11/12)
The trigger below said "instrument recall, then add L2 surgically". Here is the instrumentation, from
batch 2 (46 Tier-1 prospects) + reactivation batch 1/6 (34 accounts):

| Signal | Fired | Hit rate | Share of all detections |
|---|---|---|---|
| `new_location` | 45/80 | 56% | **88%** |
| `open_jobs` | 5/80 | 6% | 10% |
| `leadership_hire` | 1/80 | 1% | 2% |
| `funding` | **0/80** | 0% | 0% |

44% of accounts produced **zero** signals; 50% produced exactly one — and in every one of those 40 cases
it was `new_location`. So v1 was effectively a **one-signal system**, and the score was "quality of the
location signal × segment size" regardless of the four-signal formula.

**Diagnosis — the events happen; detection and windowing lost them.** Recurring causes, counted across the
80 runs: a real signal **outside its window** (16 mentions), **no publishable date** (8), **source blocked**
by 403/429/Cloudflare/expired TLS (8), **ATS portal unreadable** — Paycor/Lever/iCIMS/Workday/ADP/Paylocity
(4). Plus a structural mismatch: a 2–5-site owner-operator has **no corporate ops/finance/IT function to
hire into**, so `open_jobs` as defined cannot fire for much of the ICP.

Worth recording that the 0/80 on funding was partly a **quality** result: agents rejected a hallucinated
"$50M Series H", an unsourced "acquired by C3 Capital", an undated $10M raise and a Tracxn snippet whose
page 404'd. Widening windows must not become licence to count unverifiable events.

### Fixes applied 2026-08-12
1. **Recency is a discount, not a gate** — per-signal windows (`new_location`/`funding` 365d,
   `leadership_hire` 180d) with age decay (≤90d ×1.0 · ≤180d ×0.8 · ≤270d ×0.6 · ≤365d ×0.4) in
   `hubspot-app/scripts/score_accounts.py`. Undated-but-corroborated events now count at ×0.85 instead of
   being discarded.
2. **Permits/licences promoted to the first check for `new_location`**, with the strength rubric inverted
   so pre-opening stages outscore already-open ones, and a required `stage` field
   (`permit_filed`/`announced`/`fit_out`/`opened`). See `new_location.md`.

3. **`open_jobs` L2 BUILT — `scripts/jobs_probe.py`** (2026-08-12). The measured trigger fired, so the
   augment was built. It turned out **not** to be "wire up an Apify jobs actor": the fix is to read the
   company's **own ATS board through its public JSON API**, which is free, company-scoped by construction
   and carries post dates. Apify is now only the fallback for boards with no public API
   (Workday/iCIMS/Paycor/Paylocity/ADP/Poached). Two findings from building it:
   - **The careers page cannot be the primary source.** `insomniacookies.com` and `portillos.com` return
     403 (Cloudflare); `sweetgreen.com` renders its board in JS with no ATS string in the HTML. The probe
     therefore identifies the board by trying candidate tokens against the ATS APIs directly, never
     touching the company's site.
   - **Aggregator company-name search is unusable for scoring.** An Indeed search for `"Giordano's"`
     returned a State Farm agent named Charles Giordano, Giordano's Recycling, Giordano's Heating & Air,
     and a *different franchisee*. The probe refuses to run a name-based aggregator search.

   Result on the account that originally blocked us: Insomnia Cookies went from *"unverifiable — ADP/Lever
   portal not agent-reachable"* to **1,033 postings read, 2 above-store roles, dated, high confidence.**

### Still open
- **`leadership_hire` recall is still poor** even at 180 days; a compliant people/job-change API remains
  the deferred fix. **Not LinkedIn scraping** — see the standing rule below. (Firecrawl doesn't change
  this — LinkedIn is login-walled regardless of fetch tool, the ToS rule stands.)
- **Contraction is not yet scored.** Closures showed up repeatedly (a 3→2 footprint, a chain closing 68
  stores, a site lost to fire, several concept swaps) and currently register only as *absence* of a
  positive signal. They should actively deprioritise an account. Not built.
- **8 of the 80 measured accounts failed on 403/429/Cloudflare/expired-TLS, and several more on
  JS-rendered pages with no crawlable HTML** (see reactivation batch 2/6 run notes, 2026-08-14, for fresh
  examples). Firecrawl was added specifically for this failure mode — worth a recall re-measurement on
  the next batch to see how much of that 8+ actually clears now, before concluding it's fixed.

## MEASURED — batch 3/6, the first run with real subagents and a delta layer (2026-08-24, US repo)

> Inherited at fork-sync 2026-09-01 from cbb37d1 — all ten accounts are US. The mechanics
> (observed-vs-fired, the probe-before-dispatch rule, Firecrawl-over-REST) port; re-measure the
> per-signal rates on UKI accounts before tuning. Note open_jobs may behave differently here: the UKI
> ATS landscape (Harri/Fourth/S4labour/Flow) has no public JSON API in the probe — see `open_jobs.md`.

10 reactivation accounts, all first runs, 26 hunter dispatches. **This is the first batch where "signal"
and "fact" were actually different things**, because `state_snapshot.py` existed to tell them apart.

| Signal | Observed a real event | Fired as a signal | Note |
|---|---|---|---|
| `new_location` | **6/10** | **3/10** | 3 events were real but 243–376d old, outside `FIRST_RUN_DAYS` (180) |
| `leadership_hire` | 2/10 | **1/10** | the 1 needed the `newly_appointed` fix below to fire at all |
| `open_jobs` | 0/10 | 0/10 | **no ATS board exists on any of the ten** |
| `funding` | 0/10 | 0/10 | 10 evidenced negatives; every trap correctly rejected |

**The observed-vs-fired gap is the whole point, not a shortfall.** Six accounts have expanded recently;
three are signals *today*. With no baseline you can only trust the recent, because a 282-day-old opening
would probably have been in the baseline had one existed. Next run those become facts and the window
opens to 365. Do not "fix" this by widening `FIRST_RUN_DAYS`.

**`open_jobs` is structurally dead at this account size — now measured, not suspected.** `jobs_probe.py`
was run directly on all ten and found **no ATS board for any of them**. The diagnosis this file already
carried ("a 2–5-site owner-operator has no corporate ops/finance/IT function to hire into") is confirmed:
nine of the ten are 1–5-site owner-operators. Only the 11-site, five-state group justified a hunter, and
even there the honest answer was `present: false`. **Run the probe before dispatching this hunter** —
9 of 10 dispatches would have been pure waste.

**The 403 re-measurement this file asked for.** Firecrawl was added for the 8-of-80 access-failure mode,
and batch 3/6 put it to the test — badly. The `mcp__firecrawl__*` tools **failed on every call** with
"API key is invalid or revoked": that server carries a stale credential set outside this repo, while
`FIRECRAWL_API_KEY` in `.env` answers HTTP 200. Fixed mid-batch with **`scripts/firecrawl_fetch.py`**,
the same REST path `jobs_probe.py` already uses, which then cleared a 403 on the first try.
**Conclusion: the access-failure mode is fixable and Firecrawl does fix it — but only over REST. Do not
count the MCP tools as an access layer.** (Doubly relevant here: UKI council licensing portals are a
known 403/JS-blocked source class.)

**Quality: three fabrications rejected, none reported.** A WebSearch AI summary asserted a company
"raised $9 million"; another fabricated an owner quote that appears in neither underlying article; and a
Crunchbase page showed a "Raised Funding Round" block containing **lorem ipsum dated 1970-01-01**, the
Unix epoch — unrendered template content presented as data. Hunters also correctly refused charity
fundraisers as money going *out*, a franchise-recruitment page, an ESOP conversion (ownership, not
funding), a landlord/operating agreement, and four namesake companies with genuine raises. This is what
the 0/80 meant by "partly a quality result", reproduced.

**Contraction showed up again and still has nowhere to go.** Four of ten accounts were closing sites
while the stack only detects growth. The "not built" item above is now the most frequently-encountered
gap in the stack.

## Decisions (2026-07-17)
- **Agent-first is still the default detector.** Instrument recall, add L2 surgically.
- **Apify token added** (`APIFY_TOKEN`, gitignored env) — the **jobs** augment is ready to wire when
  agent recall on `open_jobs` proves weak. Leadership-hire's people/job-change API stays **deferred**
  (buy only if that signal's recall is poor).
- **Sales-intel Slack app is internal-only** (HubSpot/Gong) — it **cannot** reach external signals, so it
  is *not* an L2 source.
- **UKI-first sources (this fork, 2026-08-20).** All four playbooks lead with UK/IE sources:
  premises-licence + planning applications and Companies House (new_location), **Companies House
  officer appointments** (leadership_hire — a dated primary source the US never had), Caterer.com +
  the global ATS probe with a flagged **Harri/Fourth gap** (open_jobs), Companies House SH01/PSC +
  Propel/MCA deal coverage (funding). US sources retained, tagged *(US accounts only)*.
- **No raw LinkedIn scraping** — ToS/legal; use a compliant provider if/when leadership-hire recall matters.
  **Tested against Firecrawl 2026-08-14** (in case the new premium access layer changed this): it doesn't
  — Firecrawl refuses LinkedIn URLs outright ("we do not support this site"), so `leadership_hire`'s core
  bottleneck is unchanged and this rule stands as-is, not just as an internal policy but as an external
  constraint too. Confirms the deferred people/job-change API is still the only real fix for this signal.

## When to add L2 (the trigger)
Track per signal via the feedback loop: **recall** (found vs later-confirmed-true) and **false-positive
rate**. When a signal's agent recall is consistently low — most likely `leadership_hire` — that's the
signal-specific trigger to buy its augment. Not before.
