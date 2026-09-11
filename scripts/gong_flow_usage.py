#!/usr/bin/env python3
"""Measure which Gong flows each rep ACTUALLY touches, from the Gong audit log.

WHY (2026-09-11). Gong exposes no per-flow usage: the flow detail and prospect endpoints 404/405 and
/v2/stats/activity/* returns call activity per user, nothing flow-level. But `GET /v2/logs?
logType=UserActivityLog` is an audit log of Gong UI actions, and Engage edits appear in it as
`/ajax/sequences/update-sequence` (and delete-sequence) with the flow id inside the request. Nobody
edits a dead flow, so "edited recently" is the best available proxy for "live" — good enough to
pre-fill the rep survey so the first question is a confirmation, not a memory test.

WHAT IT IS NOT. Editing is curation, not sending: the log carries no enrolment, send, open or reply
event (that vocabulary does not exist in it). A flow with no edits is NOT proven dead — a rep can run
an untouched flow for months. Absence of signal is not evidence of absence; the survey still asks.

OUTPUT
  cadences/registry/_usage.json   rep × flow: touches + first/last seen, over the window  (committed)

USAGE
  python3 scripts/gong_flow_usage.py            # last 90 days
  python3 scripts/gong_flow_usage.py --days 180

Requires only stdlib. Raw log records (which carry client IPs) are never written to disk.
"""
import argparse
import base64
import collections
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
from gtm_common import load_dotenv  # noqa: E402

REG = os.path.join(ROOT, "cadences", "registry")
OUT = os.path.join(REG, "_usage.json")
ID_RE = re.compile(r"\b\d{16,20}\b")


def known_flows():
    """id → name, from the company registry plus every per-rep draft/confirmed file."""
    flows = {}
    comp = os.path.join(REG, "_company.json")
    if os.path.isfile(comp):
        for f in json.load(open(comp))["flows"]:
            flows[f["id"]] = f["name"]
    for path in glob.glob(os.path.join(REG, "drafts", "*.json")) + glob.glob(os.path.join(REG, "*.json")):
        if os.path.basename(path).startswith("_"):
            continue
        try:
            d = json.load(open(path))
        except Exception:
            continue
        for key in ("personal", "shared_with_rep", "flows"):
            for e in d.get(key, []) or []:
                if isinstance(e, dict) and "id" in e:
                    flows[e["id"]] = e["name"]
    return flows


def pull(days, auth):
    to = datetime.now(timezone.utc)
    frm = to - timedelta(days=days)
    base = "/v2/logs?" + urllib.parse.urlencode({
        "logType": "UserActivityLog",
        "fromDateTime": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toDateTime": to.strftime("%Y-%m-%dT%H:%M:%SZ")})
    cursor, pages, seq = None, 0, []
    while True:
        url = base + (f"&cursor={cursor}" if cursor else "")
        req = urllib.request.Request("https://api.gong.io" + url, headers={"Authorization": auth})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            sys.exit(f"FATAL: log pull failed at page {pages}: HTTP {e.code} {e.read()[:160]}")
        for rec in d.get("logEntries", []):
            ep = (rec["logRecord"].get("httpRequest") or {}).get("endpointUri") or ""
            if "sequence" in ep.lower():
                # keep only what we need — the raw record carries client IPs, which never touch disk
                seq.append((rec["userEmailAddress"], rec["eventTime"][:10], ep,
                            ID_RE.findall(json.dumps(rec["logRecord"]["httpRequest"]))))
        pages += 1
        cursor = d.get("records", {}).get("cursor")
        if not cursor:
            break
        if pages % 20 == 0:
            print(f"  …{pages} pages, {len(seq)} Engage actions so far", flush=True)
    return seq, pages, frm.date().isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--days", type=int, default=90)
    args = ap.parse_args()
    load_dotenv()
    k, s = os.environ.get("GONG_ACCESS_KEY"), os.environ.get("GONG_SECRET")
    if not (k and s):
        sys.exit("FATAL: GONG_ACCESS_KEY / GONG_SECRET missing from .env")
    auth = "Basic " + base64.b64encode(f"{k}:{s}".encode()).decode()

    flows = known_flows()
    print(f"cross-referencing against {len(flows)} known flows; pulling {args.days} days of audit log…")
    seq, pages, since = pull(args.days, auth)
    print(f"  {pages} pages, {len(seq)} Engage actions")

    tally = collections.defaultdict(lambda: {"touches": 0, "first_seen": None, "last_seen": None, "actions": collections.Counter()})
    unknown = collections.Counter()
    for email, day, ep, ids in seq:
        matched = [i for i in ids if i in flows]
        if not matched:
            unknown[email] += 1
            continue
        for fid in matched:
            t = tally[(email, fid)]
            t["touches"] += 1
            t["actions"][ep.rsplit("/", 1)[-1]] += 1
            t["first_seen"] = min(t["first_seen"] or day, day)
            t["last_seen"] = max(t["last_seen"] or day, day)

    by_rep = collections.defaultdict(list)
    for (email, fid), t in tally.items():
        by_rep[email].append({"flow_id": fid, "flow": flows[fid], "touches": t["touches"],
                              "first_seen": t["first_seen"], "last_seen": t["last_seen"],
                              "actions": dict(t["actions"])})
    for email in by_rep:
        by_rep[email].sort(key=lambda e: (-e["touches"], e["last_seen"]), reverse=False)
        by_rep[email].sort(key=lambda e: (e["last_seen"], e["touches"]), reverse=True)

    json.dump({"_note": "Flows each rep EDITED in Gong Engage, from the UserActivityLog audit log "
                        "(/ajax/sequences/*). A proxy for 'live', not proof of sending: the log carries no "
                        "enrolment/send/reply events. No edits does NOT mean dead — confirm with the rep.",
               "generated": date.today().isoformat(), "window_days": args.days, "since": since,
               "engage_actions_seen": len(seq),
               "unmatched_actions_by_rep": dict(unknown),
               "by_rep": dict(by_rep)}, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"\n{os.path.relpath(OUT, ROOT)} — {len(tally)} rep×flow pairs across {len(by_rep)} people")
    for email, rows in sorted(by_rep.items(), key=lambda x: -sum(r["touches"] for r in x[1])):
        top = " · ".join(f"{r['flow'][:34]} ({r['touches']})" for r in rows[:3])
        print(f"  {email:24} {len(rows):2} flows  {top}")


if __name__ == "__main__":
    main()
