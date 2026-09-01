# Integration status — the single home for wired-vs-not

`CLAUDE.md`'s table is a summary. This is the detail, so drift has one place to live rather than being
restated in four files. **Verified 2026-08-24 in the US repo (`cbb37d1`) — the infrastructure is
SHARED** (same HubSpot portal + private app + `cadence_brief` object, same Gong instance, byte-identical
`.env`), so those verifications hold here; the UKI-only deltas are marked ⚠️ UKI inline.

## HubSpot — two separate paths, don't confuse them

**1. Private-app token (`HUBSPOT_PRIVATE_APP_TOKEN` in gitignored `.env`) — the write path.**
Fully working. This is what every script uses. Confirmed: it can read
`/crm-object-schemas/v3/schemas/2-251700583`, and it is the same token the deployed app runs on.

**2. The claude.ai HubSpot connector — read/exploration only.** Limited, and the limits matter:

| Object | Read | Write |
|---|---|---|
| COMPANY | ✅ | ✅ |
| NOTE | ✅ | ✅ |
| CONTACT, DEAL, CALL | ✅ | ❌ needs permission change |
| `p139694830_cadence_brief` | ❌ **needs re-authorization** | ❌ |

So the connector **cannot currently read the object the agent writes to** — you can't audit briefs
through it. Use the private-app token, or `hs`.

**`hs` CLI:** installed (8.12.0) and **authenticated** — `~/hubspot.config.yml`, portal `139694830`,
account `nory-prod`. Note the config is at `~/hubspot.config.yml`, *not* `~/.hscli.config.yml`; checking
the wrong path makes it look unauthenticated. `hs project upload` works.

**Live object:** `p139694830_cadence_brief`, objectTypeId `2-251700583`, 68 properties of which **36 are
custom** and in sync with `hubspot-app/schema/cadence_brief.schema.json`.

## Gong — wired, but only for what it actually returns

`scripts/gong_pull.py`, Basic auth from `GONG_ACCESS_KEY` + `GONG_SECRET`. Retrieves **call metadata and
verbatim transcripts**. Writes to `output/gong/` (gitignored, real PII).

**It does not and cannot retrieve sequence analytics** — reply, open, meeting-booked rates by step.
**Gong Engage is not enabled**, so that data does not exist anywhere. Do not specify work against it;
`knowledge/gong_evidence/_sequence_performance.md` is the record of that gap. Cadence rhythm is therefore
a best-practice hypothesis, not evidence-tuned, and any deliverable leaning on it should say so.

Two data-quality facts worth knowing before trusting a transcript:
- **54 of 226 transcripts are truncated** at 12,000 characters, keeping the beginning and discarding the
  end — where the objection usually is.
- **61% of 12,955 bulk-pulled calls have `scope: Unknown`**, which is the likely cause of the
  participant-domain confirmation dropping every candidate on 11 accounts.

## Firecrawl — wired, credit-budgeted

Premium plan, added 2026-08-14. `FIRECRAWL_API_KEY` in `.env`. Available three ways: hosted MCP
(`.mcp.json`), the `firecrawl` CLI, and direct REST from `scripts/jobs_probe.py:156-260`.

**Deliberately not the default.** It exists for one failure mode: sites that are JS-rendered or that
block a plain fetch outright — 403/429/Cloudflare/expired-TLS killed 8+ of 80 measured accounts.
`jobs_probe.py` spends **one credit on one URL** (`/careers`) and only after the cheaper paths fail.
Keep it that way; it is a paid tool.

## Apify — wired, off by default

`APIFY_TOKEN` in `.env`. `jobs_probe.py:390-410`, behind `--apify`. The **T2 fallback only**, for ATS
boards with no public JSON API (Workday, iCIMS, Paycor, Paylocity, ADP, Poached).

⚠️ **Known defect:** the actor is `misceres~indeed-scraper` but it is fed a non-Indeed `startUrls` (the
company's careers page), so it will not return `positionName` items. The failure surfaces silently as
`roles == []` → `present: false`. Fix the actor choice or the input before relying on this path.

Standing rule from the measured runs: **never a name-based aggregator search.** Searching Indeed for
`"Giordano's"` returned a State Farm agent named Charles Giordano, a recycling company, an HVAC company
and a *different franchisee*. `jobs_probe.py` refuses to do it, on purpose.

## Clay — live, and owned by someone else

Workspace **"Nory Lab"** is connected via the claude.ai connector. `CLAUDE.md` claimed until 2026-08-24
that "Clay platform dropped" — that was false.

It actively owns COMPANY properties: **2,360 companies** carry `triggers_score`, most recently written
2026-08-24. Also `icp_score`, `vertical`, and the `expansion_news_* / financial_news_* /
franchising_news_* [enrichment][signals]` family.

**Treat as read-only.** The agent writes nothing to COMPANY. Clay is also the obvious candidate for the
`leadership_hire` L2 gap (`_signal_stack.md` calls it the weakest signal) — but that's a conversation
with whoever owns the workspace, not a unilateral wire-up.

Empty but purpose-built, noted in case the write-target decision is ever revisited:
`signal_last_type` (enum whose four options are exactly our four Tier-1 signals) and `signal_last_date`
— **0 records** on both.

## Connected and unused

**Google Drive / Sheets** — works. No deliverable goes here any more; the PDF path was retired
2026-08-24 (US decision, inherited). ⚠️ UKI: **the UKI entry sheet does not exist yet** — open question
#5 in `README.md`; create it to `input/README.md`'s schema with data-validation dropdowns from day one
(the US template's lack of them is a recorded defect, don't copy it).

**Slack** — connected, no channel chosen, nothing sends. The weekly digest it was for is dropped.

**Supermetrics** — connected. Its Gong path is gated behind early access and is irrelevant: we go direct
to the Gong REST API.

## NotebookLM — perimeter rule, read before any upload

Two accounts exist: personal, and `pablo@nory.ai` (created 2026-08-24). **Only the Nory notebook may
receive anything from this repo.**

The risk is operational, not theoretical: `nlm` has **one machine-wide default profile** and no command
tells you which account it writes to. Verified 2026-08-24, profile `default` → the **personal** account.
So check before **every** upload:

```
nlm login --check          # prints profile + account
nlm login switch <profile> # change the global default
```

`output/reactivation/*` and `output/gong/*` are gitignored because they are real prospect PII — closed-lost
reasons, deal amounts, contact emails, verbatim transcripts. Prefer uploading digests over raw bundles.

### The perimeter covers the WHOLE repo, not just `output/` — measured 2026-08-24

Checked before the first upload rather than assumed: **11 files in the method layer name real prospects.**
The signal playbooks, `feedback_log.md`, `_signal_stack.md`, both agent files that cite worked examples,
and even the tests (`www.machapresso.com` is a regression fixture). That is *why* the docs are good — they
record what was measured on named accounts — but it means there is **no tier of this repo that is safe for
the personal notebook**, not merely no safe part of `output/`. The profile gate applies to everything.

### The live notebooks

| | |
|---|---|
| US notebook | **US GTM Cadence Agent** — `31734816-f21a-4808-8aad-500157fa1689` (the US repo's corpus) |
| UKI notebook | ⚠️ **does not exist yet** — create it on `pablo@nory.ai` (profile `nory`) before the first UKI upload; never add UKI material to the US notebook |
| Doctrine library | **The Perfect Multi-Agent** — `432c1b79-b235-426a-923f-397934cd6b06` (agent-building research; feeds the `agent-doctrine` skill) |

US corpus uploaded 2026-08-24 after `nlm login --check` confirmed profile `nory` → `pablo@nory.ai`.

**NotebookLM rejects `.json`** ("Unsupported file type"), which killed 15 of the first 60 attempts — the 5
conjunctural registers and the 10 digests. Rendering them to markdown fixed it and is the better shape
anyway: a retrieval layer indexes prose, and raw JSON structure is noise around the sentences that carry
the meaning. If you add sources later, convert first.

**Deliberately NOT uploaded:** the 119 raw bundles (11 MB) and `output/gong/` (10 MB, 12,955 calls). The
digests already carry the substantive transcripts with the tail preserved, so the raw files add volume
without retrieval value. Never `.env`.

**What it is for, and what it is not.** It answers *semantic questions over the accumulated corpus* —
"which incumbent tools do prospects actually name, and what did they say", "how many deals died because
our own rep left". Nothing else in the stack can do that. It is **not** the agent's operational memory:
`CLAUDE.md` and `.claude/reference/` load into context automatically and the agent needs the *exact
string* (a Gong flow name, a HubSpot property), which a synthesis will not reliably give. Structured
questions stay in Python — that is how the closed-won audit and the truncation count were answered.

## Secrets

Single source: a gitignored `.env` at the repo root, auto-loaded by the scripts. The repo carries
`.env.example` and `.mcp.json.example` with placeholders only. Never in `settings.json`, never in a
tracked file.

⚠️ `.env` is currently **byte-identical between this repo and `gtm-cadence-agent-eu`** — the same portal
token and Gong keys in two working trees.
