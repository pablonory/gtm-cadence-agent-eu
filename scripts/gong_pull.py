#!/usr/bin/env python3
"""
gong_pull.py — pull calls + transcripts from the Gong REST API for Stage 2b.

PRIMARY Stage-2b source: the Supermetrics Gong connector is gated behind early access,
so we go direct to the Gong REST API (Basic auth: Access Key + Secret).

Credentials — set in your GITIGNORED env, never commit:
    export GONG_ACCESS_KEY="..."
    export GONG_SECRET="..."
    export GONG_API_BASE="https://api.gong.io"   # optional; this is the default

Usage:
    python scripts/gong_pull.py --from 2026-01-01 --to 2026-07-17
    python scripts/gong_pull.py --from 2026-01-01 --to 2026-07-17 --transcripts

Output (gitignored — holds real call data / PII): output/gong/
    calls_<from>_<to>.json          call metadata (parties, timing, deal links)
    transcripts_<from>_<to>.json    verbatim transcripts (with --transcripts)

Stdlib only — no pip install required. The Stage-2b agents (ga_gong_call_analyst,
ga_gong_sequence_analyst, ga_win_loss_synthesizer) read output/gong/ to build the
evidence packs in knowledge/gong_evidence/.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

def _load_dotenv():
    """Load KEY=VALUE lines from a gitignored .env at the repo root. Real env vars win (setdefault)."""
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()

API_BASE = os.environ.get("GONG_API_BASE", "https://api.gong.io").rstrip("/")
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "gong"))


def _auth_header():
    key = os.environ.get("GONG_ACCESS_KEY")
    secret = os.environ.get("GONG_SECRET")
    if not key or not secret:
        sys.exit("ERROR: set GONG_ACCESS_KEY and GONG_SECRET in your gitignored env. See scripts/README.md")
    token = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return f"Basic {token}"


def _iso(day):
    """YYYY-MM-DD -> RFC3339 UTC (Gong wants an ISO datetime)."""
    return datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat()


def _request(method, path, body=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", _auth_header())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"Gong API {e.code} on {method} {path}: {e.read().decode()[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"Gong API connection error on {method} {path}: {e}")


def list_calls(frm, to):
    """GET /v2/calls, paginated via records.cursor."""
    calls, cursor = [], None
    while True:
        params = {"fromDateTime": frm, "toDateTime": to}
        if cursor:
            params["cursor"] = cursor
        resp = _request("GET", "/v2/calls?" + urllib.parse.urlencode(params))
        calls.extend(resp.get("calls", []))
        cursor = resp.get("records", {}).get("cursor")
        if not cursor:
            break
        time.sleep(0.3)  # be polite to rate limits
    return calls


def get_transcripts(frm, to):
    """POST /v2/calls/transcript, paginated via records.cursor."""
    out, cursor = [], None
    while True:
        body = {"filter": {"fromDateTime": frm, "toDateTime": to}}
        if cursor:
            body["cursor"] = cursor
        resp = _request("POST", "/v2/calls/transcript", body)
        out.extend(resp.get("callTranscripts", []))
        cursor = resp.get("records", {}).get("cursor")
        if not cursor:
            break
        time.sleep(0.3)
    return out


def main():
    ap = argparse.ArgumentParser(description="Pull Gong calls + transcripts for Stage 2b.")
    ap.add_argument("--from", dest="frm", required=True, help="start date YYYY-MM-DD")
    ap.add_argument("--to", dest="to", required=True, help="end date YYYY-MM-DD")
    ap.add_argument("--transcripts", action="store_true", help="also pull verbatim transcripts")
    args = ap.parse_args()

    frm, to = _iso(args.frm), _iso(args.to)
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Gong API {API_BASE} — pulling calls {args.frm}..{args.to}")

    calls = list_calls(frm, to)
    cpath = os.path.join(OUT_DIR, f"calls_{args.frm}_{args.to}.json")
    with open(cpath, "w") as f:
        json.dump(calls, f, indent=2)
    print(f"  {len(calls)} calls -> {cpath}")

    if args.transcripts:
        transcripts = get_transcripts(frm, to)
        tpath = os.path.join(OUT_DIR, f"transcripts_{args.frm}_{args.to}.json")
        with open(tpath, "w") as f:
            json.dump(transcripts, f, indent=2)
        print(f"  {len(transcripts)} transcripts -> {tpath}")

    print("Done. Stage-2b agents read output/gong/ (gitignored — real call data).")


if __name__ == "__main__":
    main()
