#!/usr/bin/env python3
"""Gather everything needed to analyse a lost/disqualified deal for the reactivation-deal feature.

WHAT THIS IS FOR
    The Cadence Brief's new "Reactivation" tab needs an honest answer to "why did this die last time,
    and what should the first touch say differently now?" — grounded in the deal record, real Gong call
    transcripts, and logged emails, never guessed. This script does the DETERMINISTIC fetch-and-match
    work; a separate agent step (see directives, "reactivation deal analysis" runbook) reads the bundle
    it produces and writes the actual synthesis (why it died, themes, the recommended re-engagement
    angle) onto the cadence_brief record. Same split as the rest of this pipeline: Python fetches and
    scores, Claude reasons and writes prose.

WHY A SEPARATE BUNDLE STEP, NOT ONE SCRIPT END TO END
    Matching Gong calls to an account is NOT reliable by title alone — tested 2026-08-13: a title
    pre-filter for "pies" (chasing Corner Booth Holdings / Pies 'n' Thighs) also matched "Bowen Pies" and
    "Donald's Pies", two unrelated accounts. So every title-matched call is CONFIRMED by checking its real
    participant email domains via /v2/calls/extensive before its transcript is pulled. That confirm step,
    plus deal-property discovery (property names vary by portal/pipeline), is worth isolating from the
    write path so a bad match never reaches HubSpot.

REQUIRES the `crm.objects.deals.read` and `sales-email-read` scopes on HUBSPOT_PRIVATE_APP_TOKEN — added
2026-08-13 (see hubspot-app/src/app/app-hsmeta.json). Also GONG_ACCESS_KEY/GONG_SECRET for the Gong half.
Both auto-load from the repo-root .env.

USAGE
    python3 scripts/reactivation_bundle.py <domain> [--company "Name"] [--gong-refresh] [--gong-months 24]

OUTPUT (gitignored — real deal/call/email content, see .gitignore)
    output/reactivation/<domain>.json
"""
import argparse
import base64
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(HERE, "..")
OUT_DIR = os.path.join(REPO_ROOT, "output", "reactivation")
GONG_CACHE_DIR = os.path.join(REPO_ROOT, "output", "gong")


def _load_dotenv():
    path = os.path.join(REPO_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

HS_TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
GONG_KEY = os.environ.get("GONG_ACCESS_KEY")
GONG_SECRET = os.environ.get("GONG_SECRET")
GONG_BASE = os.environ.get("GONG_API_BASE", "https://api.gong.io").rstrip("/")

# Deal-stage labels that mean "this deal is dead" regardless of the portal's exact stage IDs. Resolved
# properly below via the Pipelines API (isClosed + probability 0), this list is only a label fallback.
DEAD_STAGE_HINTS = re.compile(r"closed.?lost|disqualif", re.I)

# Deal property names across common HubSpot setups that might hold the "why it died" text. We request
# every property whose NAME matches this and report whichever ones actually came back populated — never
# assume a single canonical property name, since custom pipelines vary it.
REASON_PROP_HINTS = re.compile(r"reason|lost|disqualif|closed_lost|why", re.I)

STOP_WORDS = {"the", "and", "inc", "llc", "co", "corp", "company", "group", "restaurant", "restaurants",
             "hospitality", "concepts", "enterprises", "holdings", "brands"}


# --------------------------------------------------------------------------- HubSpot
def hs_call(method, path, body=None, ok404=False):
    if not HS_TOKEN:
        sys.exit("FATAL: HUBSPOT_PRIVATE_APP_TOKEN not set.")
    req = urllib.request.Request(
        "https://api.hubapi.com" + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {HS_TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r) if r.length != 0 else {}
    except urllib.error.HTTPError as e:
        if ok404 and e.code in (404,):
            return None
        detail = e.read().decode()
        if e.code == 403 and "requires one of" in detail:
            sys.exit(f"FATAL: missing HubSpot scope for {method} {path}\n{detail}\n"
                     "Re-approve the app's scopes in HubSpot (Settings -> Integrations) and retry.")
        sys.exit(f"HubSpot API {e.code} on {method} {path}\n{detail[:400]}")


def find_company(domain):
    res = hs_call("POST", "/crm/v3/objects/companies/search", {
        "filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}],
        "properties": ["name", "domain"], "limit": 1,
    })
    results = res.get("results", [])
    return results[0] if results else None


def associated_ids(from_type, from_id, to_type):
    ids, after = [], None
    while True:
        path = f"/crm/v4/objects/{from_type}/{from_id}/associations/{to_type}?limit=200"
        if after:
            path += f"&after={urllib.parse.quote(after)}"
        res = hs_call("GET", path)
        ids += [r["toObjectId"] for r in res.get("results", [])]
        after = res.get("paging", {}).get("next", {}).get("after")
        if not after:
            return ids


def deal_property_names():
    """All deal property names on this portal, so we can fetch reason-like ones whatever they're called."""
    res = hs_call("GET", "/crm/v3/properties/deals")
    return [p["name"] for p in res.get("results", [])]


def pipeline_dead_stage_ids():
    """Stage IDs across all deal pipelines that HubSpot itself marks closed AND lost (probability 0).
    This is the correct way to find "dead" deals — never string-match a stage label, which varies by
    portal (some call it "Closed Lost", others "Disqualified", others something else entirely).
    """
    res = hs_call("GET", "/crm/v3/pipelines/deals")
    dead = set()
    for pipeline in res.get("results", []):
        for stage in pipeline.get("stages", []):
            md = stage.get("metadata", {})
            is_closed = str(md.get("isClosed")).lower() == "true"
            probability = md.get("probability")
            try:
                prob0 = float(probability) == 0.0
            except (TypeError, ValueError):
                prob0 = False
            if is_closed and prob0:
                dead.add(stage["id"])
    return dead


def read_deals(deal_ids, properties):
    out = []
    for i in range(0, len(deal_ids), 100):
        res = hs_call("POST", "/crm/v3/objects/deals/batch/read", {
            "properties": properties,
            "inputs": [{"id": str(d)} for d in deal_ids[i:i + 100]],
        })
        out += res.get("results", [])
    return out


def flag_clone_duplicates(deals):
    """Mark HubSpot "- Clone" duplicates so the analysis agent doesn't report one lost deal as two.

    Observed across the whole portal 2026-08-13: essentially every closed-lost deal has a sibling named
    "<name> - Clone", created AND closed the same day, carrying byte-identical closed_lost_reason text.
    That is a CRM/automation artifact, not a second real sales cycle — counting them separately would
    overstate how many times an account has actually been worked and lost, which is exactly the judgement
    this tab is supposed to inform. Keeps the original (earliest createdate) as primary and tags the rest.
    """
    if len(deals) < 2:
        return deals, None
    groups = {}
    for d in deals:
        p = d["properties"]
        base = re.sub(r"\s*-\s*clone\s*$", "", (p.get("dealname") or ""), flags=re.I).strip()
        key = (base.lower(), (p.get("closed_lost_reason") or "").strip())
        groups.setdefault(key, []).append(d)

    clones_found = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda d: d["properties"].get("createdate") or "")
        for dup in group[1:]:
            name = dup["properties"].get("dealname") or ""
            if re.search(r"-\s*clone\s*$", name, re.I):
                dup["properties"]["_duplicate_of"] = group[0]["id"]
                dup["properties"]["_duplicate_note"] = (
                    "Same-day '- Clone' of the primary deal with identical closed-lost reason — a CRM "
                    "artifact, NOT a separate sales cycle. Do not count as an extra loss.")
                clones_found += 1
    note = None
    if clones_found:
        note = (f"{clones_found} of {len(deals)} dead deal(s) are same-day '- Clone' duplicates with "
                "identical reason text (tagged _duplicate_of). Treat each cloned pair as ONE lost cycle.")
    return deals, note


def read_contacts(contact_ids):
    if not contact_ids:
        return []
    out = []
    for i in range(0, len(contact_ids), 100):
        res = hs_call("POST", "/crm/v3/objects/contacts/batch/read", {
            "properties": ["firstname", "lastname", "email", "jobtitle"],
            "inputs": [{"id": str(c)} for c in contact_ids[i:i + 100]],
        })
        out += res.get("results", [])
    return out


def logged_emails(contact_ids):
    """Sales emails logged to HubSpot for these contacts, via the v3 Emails engagement object.
    Requires sales-email-read. Best-effort: many teams send via a sequence tool that never logs to
    HubSpot at all, so an empty result here is expected and NOT an error — report it as "none found",
    never silently drop the section.
    """
    if not contact_ids:
        return []
    all_emails = []
    for cid in contact_ids:
        res = hs_call("GET", f"/crm/v4/objects/contacts/{cid}/associations/emails?limit=50", ok404=True)
        if not res:
            continue
        email_ids = [r["toObjectId"] for r in res.get("results", [])]
        if not email_ids:
            continue
        batch = hs_call("POST", "/crm/v3/objects/emails/batch/read", {
            "properties": ["hs_email_subject", "hs_email_text", "hs_email_direction",
                          "hs_email_status", "hs_timestamp"],
            "inputs": [{"id": str(e)} for e in email_ids],
        }, ok404=True)
        if batch:
            all_emails += batch.get("results", [])
    return all_emails


# --------------------------------------------------------------------------- Gong
def _gong_auth():
    if not GONG_KEY or not GONG_SECRET:
        return None
    return "Basic " + base64.b64encode(f"{GONG_KEY}:{GONG_SECRET}".encode()).decode()


def gong_call(method, path, body=None):
    auth = _gong_auth()
    if not auth:
        return None
    req = urllib.request.Request(GONG_BASE + path,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": auth, "Content-Type": "application/json"},
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def load_or_refresh_gong_cache(months, force_refresh):
    """Re-use the widest cached call list under output/gong/ if it's fresh enough; else pull one. This
    listing has NO participant data (see module note below) — it's only used for the cheap title
    pre-filter. Real matching happens via the per-call extensive lookup, confirmed by email domain.
    """
    os.makedirs(GONG_CACHE_DIR, exist_ok=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 31)
    frm_str, to_str = cutoff.date().isoformat(), datetime.now(timezone.utc).date().isoformat()

    if not force_refresh:
        candidates = sorted(glob.glob(os.path.join(GONG_CACHE_DIR, "calls_*.json")),
                           key=os.path.getmtime, reverse=True)
        for path in candidates:
            try:
                with open(path) as f:
                    calls = json.load(f)
                if calls and len(calls) > 50:  # a real pull, not a narrow test file
                    return calls
            except (json.JSONDecodeError, OSError):
                continue

    if not _gong_auth():
        return []
    calls, cursor = [], None
    frm_iso = cutoff.isoformat()
    to_iso = datetime.now(timezone.utc).isoformat()
    while True:
        params = {"fromDateTime": frm_iso, "toDateTime": to_iso}
        if cursor:
            params["cursor"] = cursor
        resp = gong_call("GET", "/v2/calls?" + urllib.parse.urlencode(params))
        if not resp:
            break
        calls.extend(resp.get("calls", []))
        cursor = resp.get("records", {}).get("cursor")
        if not cursor:
            break
        time.sleep(0.3)
    path = os.path.join(GONG_CACHE_DIR, f"calls_{frm_str}_{to_str}.json")
    with open(path, "w") as f:
        json.dump(calls, f, indent=2)
    return calls


def title_keywords(company_name, domain):
    """Cheap candidates to pre-filter the cached call list by title. Confirmed later by email domain —
    this step only needs to be inclusive, not precise (see the Bowen Pies / Donald's Pies false-positive
    this module note above warns about)."""
    root = domain.split(".")[0].lower()
    words = re.findall(r"[a-z0-9]+", (company_name or "").lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    out = [root]
    if words:
        out.append(" ".join(words))          # full name, for an exact-ish phrase match
        out.extend(words[:2])                 # first couple of significant words individually
    seen, uniq = set(), []
    for w in out:
        if w and w not in seen:
            seen.add(w)
            uniq.append(w)
    return uniq[:4]


def candidate_call_ids(cached_calls, keywords):
    ids = []
    for c in cached_calls:
        title = (c.get("title") or "").lower()
        if any(kw in title for kw in keywords):
            ids.append(c["id"])
    return ids


def confirm_and_enrich(call_ids, domain, known_emails):
    """For each candidate call, pull parties + trackers via /v2/calls/extensive and keep ONLY calls where
    a participant's email domain matches the account, or matches a known contact email exactly. This is
    the confirm step — title matching alone produces false positives (see module docstring).
    """
    confirmed = []
    known_emails = {e.lower() for e in known_emails if e}
    for i in range(0, len(call_ids), 20):          # batch to be polite; extensive accepts many callIds
        batch_ids = call_ids[i:i + 20]
        resp = gong_call("POST", "/v2/calls/extensive", {
            "filter": {"callIds": batch_ids},
            "contentSelector": {"exposedFields": {
                "parties": True,
                "content": {"trackers": True},
            }},
        })
        if not resp:
            continue
        for call in resp.get("calls", []):
            parties = call.get("parties", [])
            external = [p for p in parties if p.get("affiliation") == "External"]
            matched_domain = any((p.get("emailAddress") or "").lower().endswith("@" + domain)
                                for p in external)
            matched_known = any((p.get("emailAddress") or "").lower() in known_emails for p in external)
            if matched_domain or matched_known:
                trackers = [t for t in (call.get("content") or {}).get("trackers", [])
                           if t.get("count", 0) > 0]
                # Keep every party (not just external) so the transcript can be speaker-labelled —
                # a segment's speakerId only resolves to a name via the FULL parties list.
                speaker_map = {
                    p["speakerId"]: {"name": p.get("name") or "Unknown",
                                     "role": "rep" if p.get("affiliation") == "Internal" else "prospect"}
                    for p in parties if p.get("speakerId")
                }
                confirmed.append({
                    "id": call.get("metaData", {}).get("id") or batch_ids[0],
                    "external_parties": [{"name": p.get("name"), "title": p.get("title"),
                                          "email": p.get("emailAddress")} for p in external],
                    "trackers_hit": [{"name": t["name"], "count": t["count"]} for t in trackers],
                    "speaker_map": speaker_map,
                })
    return confirmed


def pull_transcripts(call_ids):
    if not call_ids:
        return {}
    out, cursor = {}, None
    while True:
        body = {"filter": {"callIds": call_ids}}
        if cursor:
            body["cursor"] = cursor
        resp = gong_call("POST", "/v2/calls/transcript", body)
        if not resp:
            break
        for ct in resp.get("callTranscripts", []):
            out[ct["callId"]] = ct.get("transcript", [])
        cursor = resp.get("records", {}).get("cursor")
        if not cursor:
            break
        time.sleep(0.3)
    return out


def flatten_transcript(transcript_segments, speaker_map=None, max_chars=12000):
    """Gong transcripts are lists of {speakerId, topic, sentences:[{text, start}]}. Flatten to
    speaker-labelled plain text (REP: ... / PROSPECT (Name): ...) using speaker_map from
    confirm_and_enrich, so the analysis agent can tell who said what rather than one run-on paragraph.
    Falls back to unlabelled if no map is given. Truncated, not summarized — the agent reads the real
    words, capped so one long call can't crowd out the rest of the bundle."""
    speaker_map = speaker_map or {}
    lines = []
    last_speaker = None
    for seg in transcript_segments or []:
        who = speaker_map.get(seg.get("speakerId"))
        label = f"{who['role'].upper()} ({who['name']})" if who else "UNKNOWN"
        text = " ".join(s.get("text", "") for s in seg.get("sentences", []))
        if not text.strip():
            continue
        if label != last_speaker:
            lines.append(f"\n{label}: {text}")
            last_speaker = label
        else:
            lines[-1] += " " + text
    out = "".join(lines).strip()
    return out[:max_chars] + (" […truncated…]" if len(out) > max_chars else "")


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("domain")
    ap.add_argument("--company", default=None)
    ap.add_argument("--gong-refresh", action="store_true", help="force a fresh Gong call-list pull")
    ap.add_argument("--gong-months", type=int, default=24)
    args = ap.parse_args()

    domain = args.domain.replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
    bundle = {"domain": domain, "generated": datetime.now(timezone.utc).date().isoformat(),
             "hubspot": {}, "gong": {}, "warnings": []}

    # --- HubSpot: company, deals, contacts, emails ---
    company = find_company(domain)
    if not company:
        bundle["warnings"].append(f"No HubSpot company found for domain '{domain}'.")
        company_name = args.company or domain.split(".")[0]
        deal_records, contact_records, email_records = [], [], []
    else:
        company_name = company["properties"].get("name") or args.company or domain.split(".")[0]
        bundle["hubspot"]["company_id"] = company["id"]
        bundle["hubspot"]["company_name"] = company_name

        deal_ids = associated_ids("companies", company["id"], "deals")
        dead_stages = pipeline_dead_stage_ids()
        prop_names = deal_property_names()
        reason_props = [p for p in prop_names if REASON_PROP_HINTS.search(p)]
        base_props = ["dealname", "dealstage", "pipeline", "amount", "closedate", "createdate",
                      "hubspot_owner_id", "hs_is_closed_won", "hs_is_closed_lost"]
        fetch_props = list(dict.fromkeys(base_props + reason_props))  # dedup, keep order

        all_deals = read_deals(deal_ids, fetch_props) if deal_ids else []
        dead_deals = [d for d in all_deals
                     if d["properties"].get("dealstage") in dead_stages
                     or str(d["properties"].get("hs_is_closed_lost")).lower() == "true"
                     or DEAD_STAGE_HINTS.search(d["properties"].get("dealstage") or "")]
        dead_deals, clone_note = flag_clone_duplicates(dead_deals)
        if clone_note:
            bundle["warnings"].append(clone_note)
        deal_records = dead_deals if dead_deals else all_deals  # fall back to "all deals" so a rep can
                                                                 # still see open/won history for context
        if not all_deals:
            bundle["warnings"].append("No deals associated with this company at all.")
        elif not dead_deals:
            bundle["warnings"].append(
                f"{len(all_deals)} deal(s) found but none read as closed/lost by pipeline stage metadata "
                "— check bundle['hubspot']['deals'] manually, stage names vary by pipeline.")

        contact_ids = associated_ids("companies", company["id"], "contacts")
        contact_records = read_contacts(contact_ids)
        email_records = logged_emails(contact_ids)
        if not email_records:
            bundle["warnings"].append("No logged HubSpot emails found for this company's contacts "
                                      "(expected if outreach went through a sequence tool that doesn't "
                                      "log to HubSpot — not necessarily a data gap).")

    bundle["hubspot"]["deals"] = [
        {"id": d["id"], **{k: v for k, v in d["properties"].items() if v is not None}} for d in deal_records
    ]
    bundle["hubspot"]["contacts"] = [
        {"id": c["id"], **{k: v for k, v in c["properties"].items() if v is not None}}
        for c in contact_records
    ]
    bundle["hubspot"]["logged_emails"] = [
        {"id": e["id"], **{k: v for k, v in e["properties"].items() if v is not None}}
        for e in email_records
    ]

    # --- Gong: title pre-filter -> email-domain confirm -> transcripts ---
    if not _gong_auth():
        bundle["warnings"].append("GONG_ACCESS_KEY/GONG_SECRET not set — skipped Gong entirely.")
    else:
        cached = load_or_refresh_gong_cache(args.gong_months, args.gong_refresh)
        keywords = title_keywords(company_name, domain)
        candidates = candidate_call_ids(cached, keywords)
        known_emails = [c["properties"].get("email") for c in contact_records]
        confirmed = confirm_and_enrich(candidates, domain, known_emails)
        bundle["gong"]["candidate_calls_by_title"] = len(candidates)
        bundle["gong"]["confirmed_calls"] = len(confirmed)
        if not confirmed:
            bundle["warnings"].append(
                f"No Gong calls confirmed for this account ({len(candidates)} title-matched candidates, "
                "0 confirmed by participant email domain). Genuinely no call history is a valid, common "
                "result — do not infer engagement level from silence alone."
            )

        call_lookup = {c["id"]: c for c in cached}
        transcripts = pull_transcripts([c["id"] for c in confirmed])
        calls_out = []
        for c in confirmed:
            meta = call_lookup.get(c["id"], {})
            calls_out.append({
                "id": c["id"],
                "url": meta.get("url"),
                "title": meta.get("title"),
                "date": meta.get("started") or meta.get("scheduled"),
                "duration_sec": meta.get("duration"),
                "external_parties": c["external_parties"],
                "trackers_hit": c["trackers_hit"],
                "transcript_text": flatten_transcript(transcripts.get(c["id"]), c.get("speaker_map")),
            })
        bundle["gong"]["calls"] = sorted(calls_out, key=lambda x: x.get("date") or "", reverse=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{domain}.json")
    with open(out_path, "w") as f:
        json.dump(bundle, f, indent=2, default=str)

    print(json.dumps({
        "file": out_path,
        "company_found": bool(company) if 'company' in dir() else False,
        "deals": len(bundle["hubspot"]["deals"]),
        "contacts": len(bundle["hubspot"]["contacts"]),
        "logged_emails": len(bundle["hubspot"]["logged_emails"]),
        "gong_calls_confirmed": bundle["gong"].get("confirmed_calls", 0),
        "warnings": bundle["warnings"],
    }, indent=2))


if __name__ == "__main__":
    main()
