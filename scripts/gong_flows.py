#!/usr/bin/env python3
"""Pull each UKI rep's Gong Engage flows and draft the per-rep flow registry.

WHY THIS EXISTS (2026-09-11). In the US the cadences are one shared 16-flow matrix, so the agent
could BUILD a flow name from vertical × persona. In UKI every rep runs their own flows on top of a
company layer, so a flow name is never built — it is LOOKED UP in that rep's registry. This script
is the capture step the US did with screenshots: it reads the Gong API and drafts the registry with
tags proposed from flow names, for a human to confirm rep by rep. Tags are proposals, not truth.

WHAT GONG GIVES US (measured 2026-09-11): GET /v2/flows?flowOwnerEmail=<rep> returns the flows that
REP can see — visibility "Company" (the shared layer, 73 flows), "Personal" (their own), and "Shared"
(other people's flows shared with them). Fields: id, name, folderName, visibility, creationDate,
exclusive. No owner field, no usage stats (detail/prospects endpoints 404/405), so creationDate is
the only in-use proxy and "is this flow live?" stays a question for the rep.

OUTPUTS
  output/gong/flows/<rep>.json          raw API pull per rep                       (gitignored — real names incl. accounts)
  cadences/registry/drafts/<rep>.json   draft registry with proposed tags — COMMITTED (Pablo 2026-09-11: flow
                                        names may live in the repo); becomes cadences/registry/<rep>.json once confirmed
  cadences/registry/REVIEW.md           one review sheet for the Phil / rep walk-through — COMMITTED, and readable
                                        in the Obsidian vault (~/nory is the vault) so it can be annotated there
  cadences/registry/_company.json       the company layer, tagged — generic templates, COMMITTED

USAGE
  python3 scripts/gong_flows.py                # all reps in cadences/uki_reps.json
  python3 scripts/gong_flows.py --rep charlie  # one rep (email prefix)

Requires only stdlib + GONG_ACCESS_KEY / GONG_SECRET in .env (lib/gtm_common.load_dotenv).
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
from gtm_common import load_dotenv  # noqa: E402

ROSTER = os.path.join(ROOT, "cadences", "uki_reps.json")
RAW_DIR = os.path.join(ROOT, "output", "gong", "flows")
DRAFT_DIR = os.path.join(ROOT, "cadences", "registry", "drafts")
REVIEW_MD = os.path.join(ROOT, "cadences", "registry", "REVIEW.md")
COMPANY_OUT = os.path.join(ROOT, "cadences", "registry", "_company.json")
TODAY = date.today().isoformat()

# ---------------------------------------------------------------- tagging heuristics (proposals)
# The agent's taxonomy is 4 verticals + pubs_bars (a UKI segment the company layer proves exists) and
# 4 personas. Gong also has IT and People personas the agent does not classify — kept as tags so the
# gap is visible, never silently mapped onto something else.
VERTICAL_RULES = [
    ("coffee_cafe", r"coffee|cafe|café"),
    ("pubs_bars",   r"\bpubs?\b|\bbars?\b|bar/pub"),
    ("qsr",         r"\bqsr"),
    ("fast_casual", r"fast casual"),
    ("fsr",         r"\bfsr\b|\bresto\b|restaurant|casual dining|\bcd\b"),
]
PERSONA_RULES = [
    ("finance",    r"finance|\bcfo\b|\bfd\b"),
    ("operations", r"\bops\b|operations|\bcoo\b|director of op|head of op|\bgm\b"),
    ("founder",    r"founder|owner"),
    ("csuite",     r"c-suite|\bceo\b|\bmd\b|md/ceo|c-level|leadership|cto\b"),
    ("it",         r"\bit\b|\bcto\b|\btech\b"),
    ("people",     r"people|\bhr\b"),
]
REACTIVATION_REASON = [
    ("no_show",        r"no show|no-show"),
    ("non_responsive", r"non-responsive|non responsive|nurture|re-engage|re engage|reengage|closing the book"),
    ("product_gaps",   r"product gap"),
    ("timing",         r"timing"),
]
EVENT_RE = re.compile(r"tech expo|level ?up|nory takes|podcast|post show|post .*party|invite|expo\b|summer party|fstec", re.I)
INBOUND_RE = re.compile(r"\bmql\b|send more info|inbound|referral", re.I)
US_MATRIX_RE = re.compile(r"^(Coffee & Cafe|Fast Casual|FSR|QSR) × (C-Suite|Finance|Founder|Operations) \((Full Suite|IM) · Tier 1\)$")
US_VERT = {"Coffee & Cafe": "coffee_cafe", "Fast Casual": "fast_casual", "FSR": "fsr", "QSR": "qsr"}
US_PERS = {"C-Suite": "csuite", "Finance": "finance", "Founder": "founder", "Operations": "operations"}


def tag(name):
    n = name.lower()
    t = {"vertical": [], "persona": [], "motion": "outbound", "suite": None}
    m = US_MATRIX_RE.match(name.strip())
    if m:  # a clone of the US matrix — fully determined by the pattern
        t.update(vertical=[US_VERT[m.group(1)]], persona=[US_PERS[m.group(2)]],
                 suite=m.group(3), source_pattern="us_matrix_clone")
        return t, "high"
    for reason, rx in REACTIVATION_REASON:
        if re.search(rx, n):
            t["motion"] = "reactivation"; t["reactivation_reason"] = reason; break
    if "reactivation" in n and "reactivation_reason" not in t:
        t["motion"] = "reactivation"
    if EVENT_RE.search(n):
        t["motion"] = "event"
    elif INBOUND_RE.search(n):
        t["motion"] = "inbound"
    for v, rx in VERTICAL_RULES:
        if re.search(rx, n): t["vertical"].append(v)
    for p, rx in PERSONA_RULES:
        if re.search(rx, n): t["persona"].append(p)
    if re.search(r"\bsmb\b", n): t["segment"] = "smb"
    if re.search(r"\bmm\b|mid-market|\bent\b|enterprise", n): t["segment"] = "mm_ent"
    classified = bool(t["vertical"] or t["persona"]) or t["motion"] != "outbound"
    if not classified:
        t["motion"] = "unclassified"  # account-specific, campaign, or personal naming — the rep must say
        return t, "low"
    conf = "high" if (t["vertical"] and t["persona"]) or t["motion"] in ("reactivation", "event", "inbound") else "med"
    return t, conf


# ---------------------------------------------------------------- Gong API
def gong_auth():
    load_dotenv()
    k, s = os.environ.get("GONG_ACCESS_KEY"), os.environ.get("GONG_SECRET")
    if not (k and s):
        sys.exit("FATAL: GONG_ACCESS_KEY / GONG_SECRET missing from .env")
    return "Basic " + base64.b64encode(f"{k}:{s}".encode()).decode()


def flows_for(email, auth):
    out, cursor = [], None
    while True:
        params = {"flowOwnerEmail": email}
        if cursor: params["cursor"] = cursor
        req = urllib.request.Request("https://api.gong.io/v2/flows?" + urllib.parse.urlencode(params),
                                     headers={"Authorization": auth})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.read().decode()[:160]}"
        out += data.get("flows", [])
        cursor = data.get("records", {}).get("cursor")
        if not cursor:
            return out, None


def entry(f, layer):
    tags, conf = tag(f["name"])
    return {"id": f["id"], "name": f["name"], "folder": (f.get("folderName") or "").strip() or None,
            "layer": layer, "created": f["creationDate"][:10], "tags": tags, "confidence": conf,
            "live": None}  # null until the rep says; the matcher only uses live: true


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--rep", help="email prefix of one rep (default: whole roster)")
    args = ap.parse_args()
    roster = json.load(open(ROSTER))["reps"]
    if args.rep:
        roster = [r for r in roster if r["email"].split("@")[0] == args.rep] or sys.exit(f"FATAL: {args.rep} not in roster")
    auth = gong_auth()
    for d in (RAW_DIR, DRAFT_DIR, os.path.dirname(COMPANY_OUT)): os.makedirs(d, exist_ok=True)

    company, review = {}, [f"# UKI flow registry — review sheet ({TODAY})\n",
        "Tags are PROPOSED from flow names. For each personal flow the rep answers: live? (yes/no) · right tags? "
        "Account-specific and event flows are excluded from the matcher automatically.\n"]
    for rep in roster:
        email = rep["email"]; slug = email.split("@")[0]
        fl, err = flows_for(email, auth)
        if fl is None:
            print(f"{slug:16} {err}"); review.append(f"\n## {rep['name']} ({email}) — PULL FAILED: {err}\n"); continue
        json.dump(fl, open(os.path.join(RAW_DIR, f"{slug}.json"), "w"), indent=1)
        personal = [entry(f, "personal") for f in fl if f["visibility"] == "Personal"]
        shared = [entry(f, "shared") for f in fl if f["visibility"] == "Shared"]
        for f in fl:
            if f["visibility"] == "Company" and f["id"] not in company: company[f["id"]] = entry(f, "company")
        draft = {"rep": email, "name": rep["name"], "role": rep["role"], "pulled": TODAY,
                 "status": "DRAFT — tags proposed from names; confirm live flows + tags with the rep before this becomes cadences/registry/<rep>.json",
                 "personal": sorted(personal, key=lambda e: e["created"], reverse=True),
                 "shared_with_rep": sorted(shared, key=lambda e: e["created"], reverse=True),
                 "company_layer": "cadences/registry/_company.json"}
        json.dump(draft, open(os.path.join(DRAFT_DIR, f"{slug}.json"), "w"), indent=1, ensure_ascii=False)
        usable = [e for e in personal if e["tags"]["motion"] in ("outbound", "reactivation")]
        review.append(f"\n## {rep['name']} — {rep['role']} ({email}) · {len(personal)} personal · {len(shared)} shared with them\n")
        if not personal and shared:
            review.append("> No `Personal`-visibility flows: this rep's own flows are among the `Shared` ones (Gong does not "
                          "report the creator). Ask them which of the shared flows are theirs — listed in the draft JSON "
                          "under `shared_with_rep`.\n")
        review.append("| live? | created | flow | folder | proposed tags | conf |\n|---|---|---|---|---|---|")
        for e in draft["personal"]:
            t = e["tags"]; tg = " ".join(filter(None, [",".join(t["vertical"]) or None, ",".join(t["persona"]) or None,
                                          t["motion"] if t["motion"] != "outbound" else None,
                                          t.get("reactivation_reason"), t.get("segment"), t.get("suite")]))
            review.append(f"| ☐ | {e['created']} | {e['name']} | {e['folder'] or ''} | {tg or '—'} | {e['confidence']} |")
        print(f"{slug:16} personal {len(personal):3} (matcher-usable {len(usable):3}) · shared {len(shared):3}")

    comp = sorted(company.values(), key=lambda e: ((e["folder"] or ""), e["name"]))
    json.dump({"_note": f"Company-visibility Gong Engage flows (the shared UKI layer + the US matrix), pulled {TODAY} "
                        "via scripts/gong_flows.py. Tags proposed from names — confirm before relying on them. "
                        "US Flows / USA Flows folders are the US agent's matrix, present here because the Gong "
                        "instance is shared; the UKI matcher must never pick them for a UKI account.",
               "pulled": TODAY, "count": len(comp), "flows": comp},
              open(COMPANY_OUT, "w"), indent=1, ensure_ascii=False)
    review.append(f"\n## Company layer — {len(comp)} flows → cadences/registry/_company.json (committed)\n")
    open(REVIEW_MD, "w").write("\n".join(review) + "\n")
    print(f"\ncompany layer: {len(comp)} flows → {os.path.relpath(COMPANY_OUT, ROOT)}")
    print(f"review sheet:  {os.path.relpath(REVIEW_MD, ROOT)}")


if __name__ == "__main__":
    main()
