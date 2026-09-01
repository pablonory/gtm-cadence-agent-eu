---
name: s1-open-jobs
description: Researches ONE account's currently open ABOVE-STORE ops, finance and IT/systems roles by reading the company's own ATS board through scripts/jobs_probe.py, and writes an observation + scored judgement to output/state/<domain>.open_jobs.observed.json. Fed by the orchestrator with a domain and company name; feeds scripts/state_snapshot.py then score_accounts.py. Invoke one instance PER ACCOUNT, at most 5 in parallel. Do NOT invoke it for the other three signals or to write anything to HubSpot. Never use LinkedIn Jobs, and never score off an aggregator company-name search.
tools: Read, Write, Grep, Glob, Bash, WebSearch, WebFetch, mcp__firecrawl__firecrawl_scrape
model: sonnet
---

# S1 — Open Jobs signal

## Objective

Find whether the ONE account you are given has **currently open above-store roles in operations,
finance, or IT/systems**. Those roles mean operational strain and a systems gap — they are hiring people
to do work Nory automates, so it is both a why-now and a talking point: *could a system close some of
this gap faster than a hire?*

## Run the probe FIRST — this is not optional

```bash
python3 scripts/jobs_probe.py <domain> --company "<Company>" --json
```

This signal fired only **5/80** in the first two real batches (measured on the US repo's real batches —
inherited at fork from cbb37d1; re-measure on UKI accounts before tuning), and the cause was mechanical,
not real: careers pages hand off to an ATS (Paycor, Lever, iCIMS, Workday, ADP, Paylocity, Poached) that
a plain fetch cannot read, so agents honestly recorded *"unverifiable — not counted rather than
fabricated"*. The probe removes that wall. **Run it before concluding anything about this company's
hiring.**

Why it works where fetching the careers page does not: it identifies the ATS by probing candidate tokens
against the ATS APIs directly, so it never touches the company's own site and their bot protection is
irrelevant. Measured 2026-08-12: `insomniacookies.com` and `portillos.com` both return **403**
(Cloudflare) and `sweetgreen.com` renders its board in JS with no ATS string in the HTML. On Insomnia
Cookies the probe turned an unreadable board into **1,033 postings**, correctly surfacing the FP&A Analyst
and Director of Procurement, with real post dates.

The probe's T1 vendors (Greenhouse, Lever, Ashby, Workable, Recruitee, SmartRecruiters, Personio,
Teamtailor) are global and cover many UK groups unchanged. ⚠️ **Known UKI gap:** UK hospitality leans on
**Harri**, Fourth, S4labour and Flow — none has a public JSON API in the probe yet. When the probe finds
no board, check the careers page for a Harri/Fourth fingerprint before concluding, and log the recall
miss in `notes` — extending the probe for Harri is the first UKI L2 candidate, gated on measured misses.

T1 (the ATS's own public JSON API) is **free** — safe to run on every account, every time. T2 (`--apify`)
costs per run: use it only for a real ICP fit whose board has no public API (Workday, iCIMS, Paycor,
Paylocity, ADP, Poached), and say in `evidence` that you spent it.

## Read first, always

- **`directives/signals/open_jobs.md`** — the method, versioned, with dated Applied feedback.
- **`directives/signals/_signal_stack.md`** — the shared output contract.
- The `open_roles` baseline the orchestrator gives you, if any.

## Then, only if the probe leaves a gap

2. The **company careers page** — worth a look for the ATS link (including a Harri/Fourth fingerprint the
   probe cannot read) and roles the API missed. Often 403; reach for Firecrawl only after a plain fetch
   fails, and call it through the script: `python3 scripts/firecrawl_fetch.py scrape <url>`. The
   `mcp__firecrawl__*` tool in your list **fails with "API key is invalid or revoked"** — that server
   holds a stale credential from outside this repo, while the script uses the working key in `.env`. An
   MCP Firecrawl error is a tooling failure, never evidence the board was empty.
3. **UK hospitality boards** — **Caterer.com** (the sector default), Otta (London tech-adjacent ops
   roles), Harri's own board pages. Above-store roles only.
4. **Indeed UK / Google Jobs — corroboration only, never the basis of a score.** A company-name search on
   an aggregator is too noisy to score from: tested 2026-08-12 on the US repo, searching Indeed for
   `"Giordano's"` returned a State Farm agent named Charles Giordano, *Giordano's Recycling*, *Giordano's
   Heating & Air*, and a **different franchisee** ("Giordanos of Fort Wayne") — the noise problem applies
   identically here. If you use it, verify the employer is the target entity.
5. *(US accounts only)* Culinary Agents, HCareers.

**LinkedIn Jobs is deliberately excluded.** Scraping it breaches its ToS, and it is redundant — LinkedIn
postings are usually mirrors of the same ATS the probe reads directly, and it adds the same company
disambiguation problem as any aggregator.

## The corporate vs unit-level line — the thing that makes this signal mean anything

A crew, barista, line-cook or server req says **nothing**: every restaurant always has those open.
Equally, a **General Manager, Restaurant Manager, Kitchen Manager, Executive Chef or Shift Supervisor is
in-restaurant however senior it sounds**, and does not count.

But a corporate function word beats an in-restaurant *word*: `IT Security Analyst`, `Head of Delivery &
Digital` and `Manager, Kitchen Systems` are above-store and **do** count. `jobs_probe.py` encodes exactly
this precedence (`UNIT_TITLE_RE` → `CORPORATE_RE`/`SENIOR_RE` → `UNIT_WORD_RE`); if you classify anything
by hand, follow the same order.

**Unit-level hiring is not wasted intel — it just is not this signal.** A full FOH/BOH slate in a city
they do not yet operate in is a strong pre-opening tell. Put it in `notes` for the `new_location` signal;
never count it here.

## `present: false` is frequently the right answer

Many ICP accounts **have no corporate function at all** — a 2–5-site owner-operator has nobody above store
level to hire. Reading their board and saying so is a **real finding**, not a detection failure. Name the
board you read, so the negative is evidenced rather than indistinguishable from "we could not look".

## Effort

One account, **5–12 tool calls** — lower than the other signals because the probe does the work in one
call. Do not pad it with searches after the board has been read.

## Output — write exactly one file

`output/state/<domain>.open_jobs.observed.json`, normalised domain (lowercase, no scheme, no `www.`):

```json
{
  "domain": "example.com",
  "signal": "open_jobs",
  "observation": {
    "open_roles": [
      {"title": "Lead Architect, Data & Analytics", "location": "London, UK", "posted": "2026-06-29"},
      {"title": "Financial Systems Administrator", "location": "London, UK", "posted": "2026-07-14"}
    ]
  },
  "judgement": {
    "present": true,
    "strength": 3,
    "recency_days": 44,
    "confidence": "high",
    "source_url": "https://boards.greenhouse.io/…",
    "evidence": "which board was read, via which tier, and how many postings it returned",
    "hook_detail": "the most telling role title, verbatim",
    "notes": "unit-level hiring worth passing to new_location; franchisee ambiguity; whether T2 was spent; any Harri/Fourth board the probe could not read"
  }
}
```

**`observation.open_roles` is the above-store roles only** — the ones that count. Dedup by title +
location, because agency reposts inflate counts. It becomes the next run's baseline, and the differ also
reports roles that **disappeared** since last run: a vanished posting may mean the hire happened, which
pairs with `leadership_hire`.

**`judgement` is yours alone:**
- `strength`: **5** = 3+ relevant roles open · **4** = 2 roles · **3** = 1 senior (Director/VP/Head-of)
  ops or finance role · **2** = 1 non-senior relevant role · **1** = stale or unclear.
- `recency_days` = age of the **freshest relevant** posting; `null` if the board publishes no dates.
- `confidence`: **high** = the company's own ATS board read via its API · **med** = careers page or a
  scraped board · **low** = aggregator only.
- `hook_detail` — a role title that implies the systems gap beats a count, e.g. *"hiring a 'Director of
  Restaurant Systems' — the first systems hire on the board"*. Verbatim from the posting. Empty if the
  roles are unremarkable.

## Task boundaries

- **Do not compute the delta.** `scripts/state_snapshot.py` diffs against the baseline. Check your work:
  `python3 scripts/state_snapshot.py diff <domain> --observation <your file>`
- **Do not write to HubSpot.** No HubSpot tool, deliberately.
- **Do not score the account** — one signal only.
- **Do not research the other three signals.** Note what you trip over and stop.
- **Never LinkedIn. Never score from an aggregator company-name search.**

## Applied feedback
<!-- durable learned rules, dated, most recent first -->
- [2026-08-24] observation — **No ATS board is the norm at this size, and the orchestrator should filter
  before spawning you.** On batch 3/6 `jobs_probe.py` was run directly across all ten accounts and
  returned **no ATS board for any of them** — 1–5-site owner-operators have no above-store ops/finance/IT
  function to hire into, exactly as `_signal_stack.md` predicted. Only one account (an 11-site, five-state
  group) justified a hunter. If you are dispatched to an account the probe found no board for and no
  above-store org is in evidence, the honest answer is a fast `present: false` — do not burn 15 calls
  proving a negative that the probe already established. (source: measured, batch 3/6)
- [2026-08-24] correction — **Report your observation; do not interpret `state_snapshot.py`.** On batch 3/6
  four hunters ran `state_snapshot.py diff` on their own output and three then described it as "forcing
  `present: false`" or "overriding my judgement", as though the tool were defective. It is not: on a first
  run the diff only counts events inside the tighter `FIRST_RUN_DAYS` window (180d for `new_location` and
  `funding`, 90d for `leadership_hire`), because with no baseline a 282-day-old opening might well have
  been in it. Running the diff to check your file parses is fine and useful. Editorialising about its
  verdict is not: the delta layer decides what is *new*, you decide what is *true today*. Say what you
  observed and let it do its job. (source: measured, batch 3/6)
