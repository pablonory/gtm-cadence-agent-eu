#!/usr/bin/env python3
"""Contact → flow mapping for one Cadence Brief (runs after upsert_brief.py).

For an account already in the cadence_brief object, this pulls EVERY contact
associated with the matching HubSpot company, classifies each job title into the
four personas (rules in cadences/UKI_FLOWS.md), and groups them under the exact
Gong flow name for the account's vertical (UKI flows pending — see UKI_FLOWS.md). Result goes to the brief's
`contacts_json` property and every mapped contact is associated to the brief —
so on MM/ENT accounts the rep sees which flow to run for which people, not just
one persona per account.

Usage:
    python3 map_contacts.py <domain>            # map + write back
    python3 map_contacts.py <domain> --dry-run  # print the map, write nothing

Rules enforced here:
- Titles are classified by pattern, in priority order Founder > C-Suite >
  Finance > Operations (so "Founder & CEO" → Founder, per the founder-led rule).
- A title that matches nothing (GM, marketing, chef, …) goes to `unmapped` —
  listed for the rep, never guessed into a flow.
- Contacts with no job title in the CRM go to `unmapped` with that reason.
- Flow names are built from the brief's vertical + the persona and MUST match
  the US Flow pattern — same regex as upsert_brief.py, fail loud if not.

Auto-loads the repo-root .env (same convention as scripts/gong_pull.py).
Requires only stdlib.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

BASE = "https://api.hubapi.com"
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv():
    path = os.path.join(HERE, "..", "..", ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()
TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")

VERTICAL_LABELS = {
    "coffee_cafe": "Coffee & Cafe",
    "fast_casual": "Fast Casual",
    "fsr": "FSR",
    "qsr": "QSR",
}
PERSONA_LABELS = {"founder": "Founder", "csuite": "C-Suite", "finance": "Finance", "operations": "Operations"}
SUITE = {"founder": "Full Suite", "csuite": "Full Suite", "finance": "IM", "operations": "IM"}

# Priority order matters: Founder outranks C-Suite ("Founder & CEO" is founder-led),
# C-Suite outranks Finance (CFO = C-Suite per UKI_FLOWS.md), Finance before Operations.
PERSONA_PATTERNS = [
    ("founder", re.compile(r"founder|owner|proprietor", re.I)),
    ("csuite", re.compile(r"\bchief\b|\bc\.?e\.?o\.?\b|\bc\.?o\.?o\.?\b|\bc\.?f\.?o\.?\b|\bc\.?t\.?o\.?\b"
                          r"|president|managing director", re.I)),
    ("finance", re.compile(r"financ|controller|accounting|fp&a|treasur", re.I)),
    ("operations", re.compile(r"operat|\bops\b|district manager|area manager|regional (manager|director)", re.I)),
]

US_FLOW_RE = re.compile(
    r"^(Coffee & Cafe|Fast Casual|FSR|QSR) × (C-Suite|Finance|Founder|Operations) "
    r"\((Full Suite|IM) · Tier 1\)$"
    r"|^UKI Reactivation$"  # assumed name — confirm in cadences/UKI_FLOWS.md before first reactivation run
)
REACTIVATION_FLOW = "UKI Reactivation"  # assumed — confirm in cadences/UKI_FLOWS.md

MAX_CONTACTS_PER_GROUP = 25  # keep contacts_json within HubSpot's textarea limit


def call(method: str, path: str, body=None):
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


def resolve_object_type():
    res = call("GET", "/crm-object-schemas/v3/schemas")
    for s in res.get("results", []):
        if s.get("name") == "cadence_brief":
            return s["objectTypeId"]
    sys.exit("FATAL: cadence_brief schema not found.")


def search_one(object_type, prop, value, properties=None):
    res = call("POST", f"/crm/v3/objects/{object_type}/search", {
        "filterGroups": [{"filters": [{"propertyName": prop, "operator": "EQ", "value": value}]}],
        "properties": properties or [prop],
        "limit": 1,
    })
    results = res.get("results", [])
    return results[0] if results else None


def company_contact_ids(company_id):
    ids, after = [], None
    while True:
        path = f"/crm/v4/objects/companies/{company_id}/associations/contacts?limit=500"
        if after:
            path += f"&after={urllib.parse.quote(after)}"
        res = call("GET", path)
        ids += [r["toObjectId"] for r in res.get("results", [])]
        after = res.get("paging", {}).get("next", {}).get("after")
        if not after:
            return ids


def read_contacts(ids):
    out = []
    for i in range(0, len(ids), 100):
        res = call("POST", "/crm/v3/objects/contacts/batch/read", {
            "properties": ["firstname", "lastname", "email", "jobtitle"],
            "inputs": [{"id": str(x)} for x in ids[i:i + 100]],
        })
        out += res.get("results", [])
    return out


def classify(title):
    for persona, pat in PERSONA_PATTERNS:
        if pat.search(title):
            return persona
    return None


def build_map(vertical, contacts, reactivation=False):
    """Group contacts by persona. Normally each group names its vertical × persona flow; on a
    reactivation brief every group names USA Reactivation instead (one motion, outside the matrix)
    while KEEPING the persona split — the rep still needs to know who is finance vs ops."""
    vlabel = VERTICAL_LABELS.get(vertical)
    if not vlabel and not reactivation:
        sys.exit(f"FATAL: brief has unknown vertical '{vertical}' — cannot name flows.")
    groups = {}  # persona -> [contact]
    unmapped = []
    for c in contacts:
        p = c.get("properties", {})
        name = " ".join(x for x in [p.get("firstname"), p.get("lastname")] if x) or p.get("email") or c["id"]
        title = (p.get("jobtitle") or "").strip()
        entry = {"id": c["id"], "name": name, "title": title or None, "email": p.get("email")}
        if not title:
            entry["reason"] = "no job title in CRM"
            unmapped.append(entry)
            continue
        persona = classify(title)
        if persona:
            groups.setdefault(persona, []).append(entry)
        else:
            entry["reason"] = "title matches no Tier-1 persona"
            unmapped.append(entry)

    out_groups = []
    for persona in ["founder", "csuite", "finance", "operations"]:  # stable display order
        if persona not in groups:
            continue
        flow = (REACTIVATION_FLOW if reactivation
                else f"{vlabel} × {PERSONA_LABELS[persona]} ({SUITE[persona]} · Tier 1)")
        if not US_FLOW_RE.match(flow):
            sys.exit(f"FATAL: built flow name '{flow}' fails the US Flow pattern — check UKI_FLOWS.md.")
        members = groups[persona]
        g = {"flow": flow, "persona": persona, "suite": SUITE[persona],
             "contacts": members[:MAX_CONTACTS_PER_GROUP]}
        if len(members) > MAX_CONTACTS_PER_GROUP:
            g["truncated"] = len(members) - MAX_CONTACTS_PER_GROUP
        out_groups.append(g)

    mapped = sum(len(g["contacts"]) + g.get("truncated", 0) for g in out_groups)
    return {
        "generated": date.today().isoformat(),
        "total_contacts": len(contacts),
        "mapped": mapped,
        "groups": out_groups,
        "unmapped": unmapped,
    }


def main():
    if not TOKEN:
        sys.exit("Set HUBSPOT_PRIVATE_APP_TOKEN first (or put it in the repo-root .env).")
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if len(args) != 1:
        sys.exit("Usage: python3 map_contacts.py <domain> [--dry-run]")
    domain = args[0].lower()

    object_type = resolve_object_type()
    brief = search_one(object_type, "domain", domain,
                       ["domain", "vertical", "company_name", "cadence_template"])
    if not brief:
        sys.exit(f"FATAL: no cadence_brief with domain '{domain}' — run upsert_brief.py first.")
    reactivation = brief["properties"].get("cadence_template") == REACTIVATION_FLOW

    company = search_one("companies", "domain", domain)
    if not company:
        sys.exit(f"FATAL: no HubSpot company with domain '{domain}' — nothing to pull contacts from.")

    contact_ids = company_contact_ids(company["id"])
    contacts = read_contacts(contact_ids) if contact_ids else []
    contact_map = build_map(brief["properties"].get("vertical"), contacts, reactivation)

    if dry:
        print(json.dumps(contact_map, indent=2))
        return

    call("PATCH", f"/crm/v3/objects/{object_type}/{brief['id']}",
         {"properties": {"contacts_json": json.dumps(contact_map, ensure_ascii=False)}})
    for g in contact_map["groups"]:
        for c in g["contacts"]:
            call("PUT", f"/crm/v4/objects/{object_type}/{brief['id']}/associations/default/contacts/{c['id']}", {})

    print(json.dumps({
        "brief_id": brief["id"], "domain": domain,
        "total_contacts": contact_map["total_contacts"], "mapped": contact_map["mapped"],
        "groups": {g["flow"]: len(g["contacts"]) for g in contact_map["groups"]},
        "unmapped": len(contact_map["unmapped"]),
    }, indent=2))


if __name__ == "__main__":
    main()
