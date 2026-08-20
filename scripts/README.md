# Scripts

Helper scripts. A script used by one part of the pipeline lives here; secrets come from a
gitignored env file, never hardcoded.

## Planned
- `read_sheet.py` — read + validate the accounts Google Sheet, group by rep. (May instead be done
  directly via the Google Sheets connector — decide when building the entry point.)
- `build_pdf.py` — render the per-account brief to PDF and upload to the rep's Drive folder.
- `gong_pull.py` — **BUILT — the PRIMARY Stage-2b source** (Supermetrics Gong connector is gated behind
  early access). Pulls calls + transcripts from the Gong REST API (Basic auth: `GONG_ACCESS_KEY` +
  `GONG_SECRET` from gitignored env; base `GONG_API_BASE`, default `https://api.gong.io`). Writes raw JSON
  to `output/gong/` (gitignored — real call data). Run:
  `python scripts/gong_pull.py --from 2026-01-01 --to 2026-07-17 --transcripts`. Stdlib only.
- `gong_mcp.py` — optional local MCP wrapper (only if we later want agents to query Gong live instead of
  batch-pulling via `gong_pull.py`). Not built.
- `apify_jobs.py` — **Stage-1 L2 augment.** Calls an Apify jobs actor (Indeed/LinkedIn Jobs) via the
  Apify REST API (`APIFY_TOKEN` from gitignored env) to structure open ops/finance/IT roles for the
  `open_jobs` signal. Only needed once agent WebFetch/WebSearch recall proves weak — see
  `directives/signals/_signal_stack.md`. Not an MCP.

> Stubs until we build them.
