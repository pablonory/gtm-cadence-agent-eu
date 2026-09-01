#!/usr/bin/env python3
"""Firecrawl scrape/search over the REST API — the fallback for fetch-hostile pages.

WHY THIS EXISTS
    The four s1_* signal hunters are given `mcp__firecrawl__firecrawl_*` tools, and their playbooks tell
    them to reach for Firecrawl once a plain fetch returns 403/Cloudflare or an empty JS-rendered page.
    Measured 2026-08-24 during the 3/6 batch: those MCP tools fail with "The Firecrawl API key is invalid
    or revoked" — the MCP server carries its own stale credential, configured outside this repo — while
    the FIRECRAWL_API_KEY in the repo's .env answers HTTP 200 on the same endpoint. Two agents lost their
    documented fallback on the same run (rubiconpizzaco.com and mightyo.com both 403'd), so the fallback
    was documented and unavailable at the same time.

    Fixing the MCP server's key needs a new session. This script needs neither: it is the same REST path
    `jobs_probe.py:fetch_via_firecrawl` already uses in production, exposed as a CLI so an agent with
    Bash can reach it. Prefer this over the MCP tools until CLAUDE.md's integrations table says otherwise.

WHEN TO USE IT — not before
    A plain WebFetch first, always. Firecrawl costs credits, so it is the second attempt, never the first:
    reach for it when WebFetch returned 403/429, a Cloudflare interstitial, or HTML with no content
    (a JS-rendered store locator or careers board). One shot per URL; if it fails, report the access
    failure honestly rather than retrying in a loop — an unreachable source is a real finding.

USAGE
    python3 scripts/firecrawl_fetch.py scrape <url> [--json] [--max-chars N] [--fresh]
    python3 scripts/firecrawl_fetch.py search "<query>" [--limit N] [--json]

    scrape  markdown for one known page (a store locator, a permit page, a careers board)
    search  Firecrawl's own web search, for when WebSearch itself is the thing coming back thin

EXIT CODES
    0 ok · 1 usage/config error · 2 the call failed or returned nothing (an honest "could not determine",
    NOT the same as "the fact is absent" — say which one in your observation's notes)
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from gtm_common import load_dotenv  # noqa: E402

API_ROOT = "https://api.firecrawl.dev/v2"
TIMEOUT = 60
DEFAULT_MAX_CHARS = 20000


def _post(path, payload, token):
    req = urllib.request.Request(
        API_ROOT + path, data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        hint = ""
        if e.code in (401, 402, 403):
            hint = ("  <- key rejected or out of credits; this is a CONFIG failure, not evidence "
                    "that the page has nothing on it")
        return None, "HTTP %s%s\n%s" % (e.code, hint, detail)
    except Exception as e:                                     # noqa: BLE001 - network is best-effort
        return None, "%s: %s" % (type(e).__name__, e)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape", help="markdown for one known URL")
    s.add_argument("url")
    s.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                   help="truncate markdown (default %d); 0 = no limit" % DEFAULT_MAX_CHARS)
    s.add_argument("--fresh", action="store_true",
                   help="force a live fetch instead of Firecrawl's cache")
    s.add_argument("--json", action="store_true", help="emit the raw payload")

    q = sub.add_parser("search", help="Firecrawl web search")
    q.add_argument("query")
    q.add_argument("--limit", type=int, default=5)
    q.add_argument("--json", action="store_true", help="emit the raw payload")

    a = ap.parse_args()

    load_dotenv(os.path.join(HERE, "..", ".env"))
    token = os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        print("FIRECRAWL_API_KEY is not set (repo-root .env). Cannot call Firecrawl.", file=sys.stderr)
        return 1

    if a.cmd == "scrape":
        body = {"url": a.url, "formats": ["markdown"], "onlyMainContent": True}
        if a.fresh:
            body["maxAge"] = 0
        d, err = _post("/scrape", body, token)
        if err:
            print("firecrawl scrape FAILED for %s\n%s" % (a.url, err), file=sys.stderr)
            return 2
        if a.json:
            print(json.dumps(d, indent=2)[:200000])
            return 0
        md = ((d or {}).get("data") or {}).get("markdown") or ""
        if not md.strip():
            print("firecrawl returned no markdown for %s (page may be genuinely empty)" % a.url,
                  file=sys.stderr)
            return 2
        if a.max_chars and len(md) > a.max_chars:
            md = md[:a.max_chars] + "\n\n[...truncated at %d chars — re-run with --max-chars 0 " \
                                    "if the tail matters]" % a.max_chars
        print(md)
        return 0

    d, err = _post("/search", {"query": a.query, "limit": a.limit}, token)
    if err:
        print("firecrawl search FAILED for %r\n%s" % (a.query, err), file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(d, indent=2)[:200000])
        return 0
    results = (d or {}).get("data") or []
    if isinstance(results, dict):
        results = results.get("web") or []
    if not results:
        print("no results for %r" % a.query, file=sys.stderr)
        return 2
    for i, r in enumerate(results, 1):
        print("%d. %s\n   %s\n   %s\n" % (
            i, r.get("title") or "(no title)", r.get("url") or "",
            (r.get("description") or "").replace("\n", " ")[:300]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
