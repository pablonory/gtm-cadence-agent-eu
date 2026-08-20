#!/usr/bin/env python3
"""Create (or inspect) the `cadence_brief` custom object schema in HubSpot.

Usage:
    export HUBSPOT_PRIVATE_APP_TOKEN=pat-...   # the Nory Cadence Agent app's access token
    python3 create_schema.py            # create the schema
    python3 create_schema.py --check    # just print the existing schema's ids (idempotent check)

On success prints the two values every later step needs:
  - objectTypeId          (e.g. 2-12345678)   -> used by API calls
  - fullyQualifiedName    (e.g. p1234567_cadence_brief) -> paste into
    src/app/cards/cadence-brief-card-hsmeta.json `objectTypes`.

Requires only stdlib (urllib) — no pip installs.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.hubapi.com"
TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
HERE = os.path.dirname(os.path.abspath(__file__))


def call(method: str, path: str, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"HTTP {e.code} on {method} {path}\n{detail}")


def report(schema):
    print("objectTypeId:        ", schema.get("objectTypeId"))
    print("fullyQualifiedName:  ", schema.get("fullyQualifiedName"))
    print()
    print("NEXT: paste the fullyQualifiedName into src/app/cards/"
          "cadence-brief-card-hsmeta.json -> config.objectTypes, then `hs project upload`.")


def main():
    if not TOKEN:
        sys.exit("Set HUBSPOT_PRIVATE_APP_TOKEN first (the app's access token, Settings -> Integrations).")

    existing = call("GET", "/crm-object-schemas/v3/schemas")
    found = [s for s in existing.get("results", []) if s.get("name") == "cadence_brief"]

    if "--check" in sys.argv:
        if found:
            report(found[0])
        else:
            print("cadence_brief does not exist yet — run without --check to create it.")
        return

    if found:
        print("cadence_brief already exists — nothing created.")
        report(found[0])
        return

    with open(os.path.join(HERE, "cadence_brief.schema.json")) as f:
        schema_body = json.load(f)

    created = call("POST", "/crm-object-schemas/v3/schemas", schema_body)
    print("Created custom object `cadence_brief`.")
    report(created)


if __name__ == "__main__":
    main()
