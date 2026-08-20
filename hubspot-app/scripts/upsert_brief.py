#!/usr/bin/env python3
"""Upsert one Cadence Brief record — the agent's write path (BUILD_SPEC B2–B4).

Usage:
    export HUBSPOT_PRIVATE_APP_TOKEN=pat-...
    python3 upsert_brief.py brief.json

brief.json shape (produced by the pipeline; only rep_email + properties are required):
{
  "rep_email": "marcus.hale@nory.ai",          <- sheet's Rep column; becomes hubspot_owner_id
  "company_domain": "rowanoakgroup.com",       <- association target (matched in HubSpot)
  "contact_email": "dana@rowanoakgroup.com",   <- optional; associates the persona contact
  "properties": {
      "company_name": "Rowan & Oak",
      "domain": "rowanoakgroup.com",
      "batch": "UKI batch 1",                  <- which input batch this row came from (filterable)
      "score": 84, "score_band": "high", "status": "ready",
      "vertical": "fsr", "persona": "finance", "locations": 11,
      "why_now": "...", "signals_json": "[...]",
      "brief_json": "{...}",   <- STRUCTURED guidance the card renders instead of prose. Shape:
                               --   {why_now{headline,points[]}, coordinate{owner,last_contacted,
                               --    days_ago,deals,note}, corrections[], copy_rationale{hook,proof,
                               --    persona,vertical}}. Keep why_now/first_touch_rationale too (they
                               --    are the fallback + the digest source), but put the SCANNABLE
                               --    version here — one fact per bullet, one sentence per field.
      "first_touch_subject": "...", "first_touch_body": "...",
      "first_touch_alt_subject": "...", "first_touch_alt_body": "...",
      "first_touch_rationale": "...", "evidence_backed": "true",
      "anti_ai_passed": "true",
      "first_touch_basis": "account_signal|conjunctural|vertical_pain",  <- see needs_conjunctural in
                                                                         --    score_accounts.py output
      "conjunctural_signal": "mw-ca-2027-01: CA fast-food wage step",   <- only when basis=conjunctural
      "cadence_template": "FSR × Finance (IM · Tier 1)",
      "gong_template_url": "https://...", "last_run": "2026-08-10"
  }
}

Rules enforced here (from input/README.md + BUILD_SPEC):
- rep_email MUST resolve to a HubSpot owner — otherwise the brief is orphaned. We FAIL, not guess.
- Upsert key = domain (unique property on cadence_brief).
- batch is the input-run label (free text, straight from the sheet's Batch column). It is only WARNED
  about, not required — an unlabelled brief is still valid, just harder to filter later.
- cadence_template must look like a real, confirmed flow name (see cadences/UKI_FLOWS.md) — warned if
  not; while UKI flows are unconfirmed, leave it EMPTY ("flow pending").

Requires only stdlib.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.hubapi.com"


def _load_dotenv():
    """Auto-load the gitignored repo-root .env, matching map_contacts.py / reactivation_bundle.py.
    Without this the script only worked if the caller exported the token by hand, which is a footgun
    every time the app is reinstalled and HubSpot rotates the token. Real env vars still win.
    """
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()
TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
OBJECT = None  # resolved at runtime to the portal's objectTypeId (e.g. 2-251700583) — see resolve_object_type()

US_FLOW_RE = re.compile(
    r"^(Coffee & Cafe|Fast Casual|FSR|QSR) × (C-Suite|Finance|Founder|Operations) "
    r"\((Full Suite|IM) · Tier 1\)$"
    r"|^UKI Reactivation$"  # assumed name — confirm in cadences/UKI_FLOWS.md before first reactivation run
)


def call(method: str, path: str, body=None, ok404=False):
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
        if ok404 and e.code == 404:
            return None
        sys.exit(f"HTTP {e.code} on {method} {path}\n{e.read().decode()}")


def resolve_object_type():
    """Short names don't resolve on CRM API calls — look up cadence_brief's objectTypeId once."""
    res = call("GET", "/crm-object-schemas/v3/schemas")
    for s in res.get("results", []):
        if s.get("name") == "cadence_brief":
            return s["objectTypeId"]
    sys.exit("FATAL: cadence_brief schema not found — run hubspot-app/schema/create_schema.py first.")


def resolve_owner(email):
    """Rep email -> hubspot owner id. A typo orphans the cadence: fail loud (input/README.md)."""
    res = call("GET", f"/crm/v3/owners?email={urllib.parse.quote(email)}")
    owners = res.get("results", [])
    if not owners:
        sys.exit(f"FATAL: no HubSpot owner for rep email '{email}'. "
                 "Fix the sheet's Rep column — not guessing an owner.")
    return owners[0]["id"]


def search_one(object_type, prop, value):
    res = call("POST", f"/crm/v3/objects/{object_type}/search", {
        "filterGroups": [{"filters": [{"propertyName": prop, "operator": "EQ", "value": value}]}],
        "limit": 1,
    })
    results = res.get("results", [])
    return results[0]["id"] if results else None


def associate(brief_id, to_type, to_id):
    # v4 default association (unlabeled)
    call("PUT", f"/crm/v4/objects/{OBJECT}/{brief_id}/associations/default/{to_type}/{to_id}", {})


def main():
    global OBJECT
    if not TOKEN:
        sys.exit("Set HUBSPOT_PRIVATE_APP_TOKEN first.")
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 upsert_brief.py brief.json")
    OBJECT = resolve_object_type()

    with open(sys.argv[1]) as f:
        brief = json.load(f)

    props = dict(brief["properties"])
    domain = props.get("domain") or brief.get("company_domain")
    if not domain:
        sys.exit("FATAL: brief has no domain (the upsert/dedup key).")
    props["domain"] = domain

    if not props.get("batch"):
        print("WARNING: brief has no `batch` label — it won't be filterable by input run. "
              "Pass the sheet's Batch column (e.g. 'Reactivation US batch 1/6').")

    flow = props.get("cadence_template", "")
    if flow and not US_FLOW_RE.match(flow):
        print(f"WARNING: cadence_template '{flow}' does not match the flow naming pattern "
              "(<Vertical> × <Persona> (<Suite> · Tier 1)) — check cadences/UKI_FLOWS.md. "
              "NOTE: while UKI flows are unconfirmed, an EMPTY cadence_template is the correct value.")

    # 1. Owner (the linchpin — record scoping keys on this)
    props["hubspot_owner_id"] = resolve_owner(brief["rep_email"])

    # 2. Upsert on domain
    existing_id = search_one(OBJECT, "domain", domain)
    if existing_id:
        call("PATCH", f"/crm/v3/objects/{OBJECT}/{existing_id}", {"properties": props})
        brief_id, action = existing_id, "updated"
    else:
        created = call("POST", f"/crm/v3/objects/{OBJECT}", {"properties": props})
        brief_id, action = created["id"], "created"

    # 3. Associations
    company_id = search_one("companies", "domain", brief.get("company_domain", domain))
    if company_id:
        associate(brief_id, "companies", company_id)
    else:
        print(f"NOTE: no HubSpot company matched domain '{domain}' — brief left unassociated.")
    if brief.get("contact_email"):
        contact_id = search_one("contacts", "email", brief["contact_email"])
        if contact_id:
            associate(brief_id, "contacts", contact_id)

    print(json.dumps({
        "brief_id": brief_id, "action": action, "domain": domain,
        "owner_id": props["hubspot_owner_id"],
        "company_associated": bool(company_id),
    }, indent=2))


if __name__ == "__main__":
    main()
