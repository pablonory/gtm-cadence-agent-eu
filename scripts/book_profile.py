#!/usr/bin/env python3
"""Profile ONE rep's HubSpot account book, to pick the segmentation axis for their flow set.

For flow design (directives/flow_design.md, in progress) we need to know, per rep, how their book
distributes across segment bands (SMB/MM/ENT, context/icp/segments.md), verticals, and — with
--contacts — the personas actually present on their ICP-fit accounts. The axis with the most
spread is the one their flows should split on.

Usage:
    python3 scripts/book_profile.py --rep louisgrenier@nory.ai
    python3 scripts/book_profile.py --rep josh@nory.ai --contacts

Outputs aggregates only (no company names, no contact PII) to output/book_profiles/<rep>.json
and prints a summary. output/ is gitignored regardless.

Honesty notes, printed with the output:
- `vertical` is the Clay-owned COMPANY property: six values disjoint from the agent's four
  verticals (one is `Pub`). Fine for AGGREGATE profiling; banned as per-account brief input
  (CLAUDE.md — classify from the sheet, HubSpot vertical is a contradiction check only).
- Size bands prefer the materialised `uki_size_band__account_map_` (account-map snapshot,
  2 Sep 2026); where empty, the band is derived from locations count per segments.md
  (SMB 2-9 · MM 10-29 · ENT 30+ · single-site = out of focus).
- Persona classification reuses map_contacts.classify (Founder > C-Suite > Finance > Ops);
  unmatched titles are listed, never guessed.

Stdlib only, Python 3.9. Reads HUBSPOT_PRIVATE_APP_TOKEN from the repo .env via lib/gtm_common.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, os.path.join(HERE, "..", "hubspot-app", "scripts"))
from gtm_common import load_dotenv  # noqa: E402
from map_contacts import classify  # noqa: E402  (one classifier, everywhere)

load_dotenv(__file__)
TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
BASE = "https://api.hubapi.com"
SLEEP = 0.25  # shared portal — stay polite (reactivation_bundle.py uses 0.3 on hot loops)

COMPANY_PROPS = [
    "name", "domain", "vertical",
    "icp_fit__enrichment_",
    "uki_size_band__account_map_",
    "reactivation_account__account_map_",
    "locations_count__enriched_", "number_of_locations",
]


def call(method, path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r) if r.length != 0 else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {method} {path}\n{e.read().decode()}")


def resolve_owner(email):
    res = call("GET", f"/crm/v3/owners?email={urllib.parse.quote(email)}")
    owners = res.get("results", [])
    if not owners:
        sys.exit(f"FATAL: no HubSpot owner for '{email}' — check the address, not guessing.")
    return owners[0]["id"]


def owned_companies(owner_id):
    """Every company owned by the rep, with the profile properties. Paged search."""
    out, after = [], None
    while True:
        body = {
            "filterGroups": [{"filters": [
                {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": owner_id},
            ]}],
            "properties": COMPANY_PROPS,
            "limit": 100,
        }
        if after:
            body["after"] = after
        res = call("POST", "/crm/v3/objects/companies/search", body)
        out += res.get("results", [])
        after = res.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out
        time.sleep(SLEEP)


def locations(props):
    for key in ("locations_count__enriched_", "number_of_locations"):
        raw = (props.get(key) or "").strip()
        if raw:
            try:
                return int(float(raw))
            except ValueError:
                pass
    return None


def band(props):
    """Materialised account-map band first; else derive from locations per segments.md."""
    stamped = (props.get("uki_size_band__account_map_") or "").strip()
    if stamped:
        return stamped.upper()
    n = locations(props)
    if n is None:
        return "unsized"
    if n >= 30:
        return "ENT"
    if n >= 10:
        return "MM"
    if n >= 2:
        return "SMB"
    return "single-site"


def is_icp(props):
    verdict = (props.get("icp_fit__enrichment_") or "").strip().lower()
    return "not" not in verdict and verdict != "" if verdict else False


def contact_personas(company_ids, cap):
    """Persona distribution across the contacts of up to `cap` companies (ICP-fit, largest first
    upstream). Aggregates only."""
    persona_counts = Counter()
    unmapped_titles = Counter()
    no_title = 0
    contact_ids = []
    for i in range(0, min(len(company_ids), cap), 100):
        chunk = company_ids[i:i + 100]
        res = call("POST", "/crm/v4/associations/companies/contacts/batch/read",
                   {"inputs": [{"id": str(c)} for c in chunk]})
        for row in res.get("results", []):
            contact_ids += [t["toObjectId"] for t in row.get("to", [])]
        time.sleep(SLEEP)
    contact_ids = list(dict.fromkeys(contact_ids))
    for i in range(0, len(contact_ids), 100):
        res = call("POST", "/crm/v3/objects/contacts/batch/read", {
            "properties": ["jobtitle"],
            "inputs": [{"id": str(x)} for x in contact_ids[i:i + 100]],
        })
        for c in res.get("results", []):
            title = (c.get("properties", {}).get("jobtitle") or "").strip()
            if not title:
                no_title += 1
                continue
            persona = classify(title)
            if persona:
                persona_counts[persona] += 1
            else:
                unmapped_titles[title.lower()] += 1
        time.sleep(SLEEP)
    return {
        "contacts_seen": len(contact_ids),
        "personas": dict(persona_counts.most_common()),
        "no_title": no_title,
        "unmapped": sum(unmapped_titles.values()),
        "top_unmapped_titles": dict(unmapped_titles.most_common(15)),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rep", required=True, help="rep email, e.g. josh@nory.ai")
    ap.add_argument("--contacts", action="store_true",
                    help="also classify contact job titles on ICP-fit accounts (slower)")
    ap.add_argument("--contacts-cap", type=int, default=150,
                    help="max ICP-fit companies to pull contacts for (largest books first)")
    args = ap.parse_args()
    if not TOKEN:
        sys.exit("FATAL: HUBSPOT_PRIVATE_APP_TOKEN not set (repo .env).")

    owner_id = resolve_owner(args.rep)
    companies = owned_companies(owner_id)

    icp = [c for c in companies if is_icp(c.get("properties", {}))]
    profile = {
        "rep": args.rep,
        "owner_id": owner_id,
        "pulled": time.strftime("%Y-%m-%d"),
        "book_total": len(companies),
        "icp_fit": len(icp),
        "reactivation": sum(
            1 for c in companies
            if (c["properties"].get("reactivation_account__account_map_") or "").strip().lower() == "yes"
        ),
        "icp_by_band": dict(Counter(band(c["properties"]) for c in icp).most_common()),
        "icp_by_vertical_clay": dict(Counter(
            (c["properties"].get("vertical") or "").strip() or "(empty)" for c in icp
        ).most_common()),
        "icp_band_x_vertical": {},
        "_notes": [
            "vertical = Clay-owned COMPANY property (6 values, disjoint from the agent's 4) — "
            "aggregate profiling only, never per-account brief input",
            "bands: materialised uki_size_band__account_map_ (2 Sep snapshot) else derived from "
            "locations per context/icp/segments.md",
        ],
    }
    cross = Counter()
    for c in icp:
        p = c["properties"]
        v = (p.get("vertical") or "").strip() or "(empty)"
        cross[f"{band(p)} | {v}"] += 1
    profile["icp_band_x_vertical"] = dict(cross.most_common())

    if args.contacts:
        ranked = sorted(icp, key=lambda c: locations(c["properties"]) or 0, reverse=True)
        profile["contacts"] = contact_personas([c["id"] for c in ranked], args.contacts_cap)
        profile["contacts"]["companies_sampled"] = min(len(ranked), args.contacts_cap)

    out_dir = os.path.join(HERE, "..", "output", "book_profiles")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, args.rep.split("@")[0] + ".json")
    with open(out_path, "w") as fh:
        json.dump(profile, fh, indent=1)

    print(f"\n{args.rep} — book {profile['book_total']} · ICP-fit {profile['icp_fit']} · "
          f"reactivation {profile['reactivation']}")
    print("\nICP by band:")
    for k, v in profile["icp_by_band"].items():
        print(f"  {k:<12} {v}")
    print("\nICP by vertical (Clay's — aggregate only):")
    for k, v in profile["icp_by_vertical_clay"].items():
        print(f"  {k:<24} {v}")
    print("\nBand × vertical (top 12):")
    for k, v in list(profile["icp_band_x_vertical"].items())[:12]:
        print(f"  {k:<32} {v}")
    if args.contacts:
        c = profile["contacts"]
        print(f"\nContacts on top {c['companies_sampled']} ICP accounts: {c['contacts_seen']} seen · "
              f"{c['no_title']} without title · {c['unmapped']} unmapped")
        for k, v in c["personas"].items():
            print(f"  {k:<12} {v}")
        print("  top unmapped titles:", ", ".join(list(c["top_unmapped_titles"])[:8]) or "—")
    print(f"\nWrote {os.path.relpath(out_path, os.path.join(HERE, '..'))}")


if __name__ == "__main__":
    main()
