#!/usr/bin/env python3
"""Stage-1 delta layer — turns an observation into a signal by diffing it against last run.

THE POINT: a buying signal is a *change*, not a fact. "They have 9 sites" is a fact. "They opened 2
sites since we last looked" is a signal. Without a stored baseline, every run re-reports the same
static facts forever, which is exactly what happened before this existed — output/state/ was specified
in directives/signals/_delta_state.md on 2026-07-17 and never written to across 109 processed accounts.

DIVISION OF LABOUR, on purpose: a signal subagent OBSERVES (web research, judgement about whether a
site really belongs to this group). This script DIFFS (set differences, date arithmetic, expiry). Set
maths and date maths are where an LLM quietly gets things wrong, so they are code.

USAGE
    # what did we know last time? (empty dict on first run)
    python3 scripts/state_snapshot.py read <domain>

    # observation -> signals, without persisting anything
    python3 scripts/state_snapshot.py diff <domain> --observation obs.json [--today YYYY-MM-DD]

    # same diff, then persist today's observation as the new baseline
    python3 scripts/state_snapshot.py commit <domain> --observation obs.json [--today YYYY-MM-DD]

OBSERVATION FILE — what the subagent produces. Every key optional; omit what you did not look for.
Omitting a key is NOT the same as observing zero: an omitted key is left untouched in the baseline,
while an explicit empty list means "I looked and there is nothing".
    {
      "locations": {"count": 11, "sites": ["Austin-Domain", "Dallas-Uptown"]},
      "execs":     [{"name": "...", "role": "COO", "start_date": "2026-06-07"}],
      "funding":   {"round": "Series A", "date": "2026-06-20", "amount": "$12m"},
      "open_roles":[{"title": "Head of Ops", "location": "NYC", "posted": "2026-07-07"}],
      "contract_expiry": "2026-10-01"
    }

OUTPUT — signal objects shaped to directives/signals/_signal_stack.md, ready for score_accounts.py.
`present` is true only when there is a NEW, UNEXPIRED delta. Strength/confidence are NOT set here:
they are the observer's judgement, and this script has no way to know how well-sourced a finding was.
The observer passes them through under "judgement" per signal if it has them.

Stdlib only. Snapshots live in output/state/<domain>.json — gitignored, real prospect data.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from gtm_common import normalize_domain  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(HERE, "..", "output", "state")

# Expiry per signal, in days. MUST match WINDOWS in hubspot-app/scripts/score_accounts.py — a signal
# that scores 0.0 there should not be reported present here. _delta_state.md still carried the
# pre-2026-08-12 values (90/180/180); these are the live ones.
EXPIRY_DAYS = {"leadership_hire": 180, "funding": 365, "new_location": 365}

# First run has no baseline, so count-diffing is impossible. Intrinsic-date signals can still fire off
# their own timestamp — but only if genuinely recent, otherwise run 1 would flag an account's entire
# history as new. Deliberately tighter than EXPIRY_DAYS.
FIRST_RUN_DAYS = {"leadership_hire": 90, "funding": 180, "new_location": 180}


def _today(arg=None):
    if arg:
        return datetime.date.fromisoformat(arg)
    return datetime.datetime.now(datetime.timezone.utc).date()


def _age_days(date_str, today):
    """Days since an ISO date. None when unparseable or absent — an undated finding, which is common
    in this segment (small US operators rarely get dated coverage) and is not an error."""
    if not date_str:
        return None
    text = str(date_str).strip()[:10]
    try:
        return (today - datetime.date.fromisoformat(text)).days
    except ValueError:
        return None


def _path(domain):
    return os.path.join(STATE_DIR, "{}.json".format(normalize_domain(domain)))


def read_state(domain):
    path = _path(domain)
    if not os.path.isfile(path):
        return {}
    with open(path) as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            # Never silently treat a corrupt baseline as "first run" — that would re-flag the account's
            # whole history as new.
            sys.exit("FATAL: {} is not valid JSON ({}). Fix or delete it deliberately.".format(path, exc))


def _site_name(site):
    """A site may arrive as a bare string or as {name, date, stage}. The subagent writes the dict form
    (it needs to carry a date per site); the baseline stores names only. Both must compare equal."""
    if isinstance(site, dict):
        return str(site.get("name") or site.get("site") or "")
    return str(site)


def _site_key(site):
    """Compare site names case- and whitespace-insensitively. Observers phrase them inconsistently
    across runs ('Austin - Domain' vs 'austin-domain'), and a formatting change is not an opening.

    Must accept both shapes: comparing a dict's repr against a stored name silently reports every
    known site as new, which is the exact failure this layer exists to prevent.
    """
    return " ".join(_site_name(site).lower().replace("-", " ").replace("_", " ").split())


def _exec_key(person):
    name = str(person.get("name", "")).strip().lower()
    role = str(person.get("role", "")).strip().lower()
    return (name, role) if name else ("", role)


def _role_key(role):
    return (
        " ".join(str(role.get("title", "")).lower().split()),
        " ".join(str(role.get("location", "")).lower().split()),
    )


def diff_new_location(baseline, obs, today, first_run):
    """Delta = sites present now that were not in the stored baseline. Count increase corroborates."""
    cur = obs.get("locations")
    if cur is None:
        return None
    cur_sites = list(cur.get("sites") or [])
    cur_count = cur.get("count")
    if cur_count is None:
        cur_count = len(cur_sites) or None

    prior = baseline.get("locations") or {}
    prior_keys = {_site_key(s) for s in (prior.get("sites") or [])}
    prior_count = prior.get("count")

    new_sites, seen = [], set()
    for site in cur_sites:
        key = _site_key(site)
        if key and key not in prior_keys and key not in seen:
            seen.add(key)
            new_sites.append(site)

    count_delta = None
    if isinstance(cur_count, int) and isinstance(prior_count, int):
        count_delta = cur_count - prior_count

    if first_run:
        # No baseline: every site looks new. Only flag openings the observer dated recently, and say so.
        dated = [s for s in cur_sites if isinstance(s, dict)]
        recent = []
        for site in dated:
            age = _age_days(site.get("date"), today)
            if age is not None and 0 <= age <= FIRST_RUN_DAYS["new_location"]:
                recent.append(site)
        return {
            "signal": "new_location",
            "present": bool(recent),
            "recency_days": min((_age_days(s.get("date"), today) for s in recent), default=None),
            "new_sites_count": len(recent),
            "total_locations": cur_count,
            "locations": [_site_name(s) for s in recent],
            "evidence": (
                "first run, no baseline: {} of {} sites dated within {}d".format(
                    len(recent), len(cur_sites), FIRST_RUN_DAYS["new_location"])
                if recent else
                "first run, no baseline: baseline seeded from {} sites, none dated recently".format(len(cur_sites))
            ),
            "first_run": True,
        }

    return {
        "signal": "new_location",
        "present": bool(new_sites),
        "recency_days": None,  # a count/set delta has no intrinsic date; observer supplies one if known
        "new_sites_count": len(new_sites),
        "total_locations": cur_count,
        "locations": [_site_name(s) for s in new_sites],
        "count_delta": count_delta,
        "evidence": (
            "{} site(s) not in last run's baseline of {}".format(len(new_sites), len(prior_keys))
            if new_sites else "no site not already in the baseline of {}".format(len(prior_keys))
        ),
        "first_run": False,
    }


def diff_leadership_hire(baseline, obs, today, first_run):
    """Delta = an exec not previously seen, whose start date is inside the window and not yet flagged."""
    cur = obs.get("execs")
    if cur is None:
        return None
    prior = {_exec_key(p): p for p in (baseline.get("execs") or [])}

    fresh, ages, incoming = [], [], []
    limit = FIRST_RUN_DAYS["leadership_hire"] if first_run else EXPIRY_DAYS["leadership_hire"]
    for person in cur:
        key = _exec_key(person)
        was_known = key in prior
        already_flagged = bool(prior.get(key, {}).get("flagged_run")) if was_known else False

        # An appointment is usually ANNOUNCED before the person starts, and the announcement is what
        # opens the buying window — so measure from announced_date when we have it. Portillo's new CFO
        # was announced Aug 4 effective Sep 7: dating from the start date made the age NEGATIVE and
        # zeroed a strength-5 signal 8 days old.
        age = _age_days(person.get("announced_date"), today)
        if age is None:
            age = _age_days(person.get("start_date"), today)
            if age is not None and age < 0:
                # Not yet in the seat. That is the sharpest window there is, not a data error: they are
                # arriving and have not chosen their tools. Score it as brand new.
                incoming.append(person.get("name"))
                age = 0
        in_window = age is not None and 0 <= age <= limit
        # Undated hires count only when the person is genuinely new to us — otherwise an undated exec
        # would re-fire every single run.
        #
        # FIRST-RUN HOLE, found on batch 3/6 (2026-08-24) and fixed by `newly_appointed`. With no
        # baseline every exec is "not was_known", so a blanket undated pass would fire on every
        # long-tenured founder who has no start_date — which is why `not first_run` was here. But it
        # swallowed the opposite case permanently: Backal Hospitality's SVP of Ops was found via a
        # Wayback diff (absent 2024-11-19, present today) with no publishable date. Run 1 dropped him for
        # being undated, commit() seeded him into the baseline UNFLAGGED, and from run 2 on he was
        # `was_known` — so he could never fire, ever.
        #
        # The observer can tell these apart even when the sources cannot date them, so let it say so:
        # `newly_appointed: true` on the exec record means "I have positive evidence this seat changed
        # hands — absence-then-presence in a dated snapshot — I just cannot pin the day." Default stays
        # unchanged, so an undated founder is still ignored on a first run. commit() then stamps
        # flagged_run on whatever surfaced, which is what stops it re-firing next week.
        undated_new = age is None and not was_known and (
            not first_run or bool(person.get("newly_appointed")))
        if already_flagged:
            continue
        if in_window or undated_new:
            fresh.append(person)
            if age is not None:
                ages.append(age)

    return {
        "signal": "leadership_hire",
        "present": bool(fresh),
        "recency_days": min(ages) if ages else None,
        "person_name": fresh[0].get("name") if fresh else None,
        "role": fresh[0].get("role") if fresh else None,
        "evidence": (
            "{} new/unflagged exec(s) within {}d{}".format(
                len(fresh), limit,
                "; {} not yet in the seat (announced, incoming)".format(len(incoming)) if incoming else "")
            if fresh else "no unflagged exec within {}d of {} known".format(limit, len(prior))
        ),
        "incoming": incoming or None,
        "first_run": first_run,
    }


def diff_funding(baseline, obs, today, first_run):
    """Delta = a round newer than the stored one, inside the window."""
    cur = obs.get("funding")
    if cur is None:
        return None
    if not cur:
        return {"signal": "funding", "present": False, "recency_days": None,
                "evidence": "no funding event observed", "first_run": first_run}

    prior = baseline.get("funding") or {}
    age = _age_days(cur.get("date"), today)
    limit = FIRST_RUN_DAYS["funding"] if first_run else EXPIRY_DAYS["funding"]

    prior_age = _age_days(prior.get("date"), today)
    is_newer = True
    if prior_age is not None and age is not None:
        is_newer = age < prior_age
    elif prior.get("round") and prior.get("round") == cur.get("round") and prior.get("flagged_run"):
        is_newer = False

    in_window = age is not None and 0 <= age <= limit
    # Undated raises were a real source of noise: the 0/80 measured result was partly agents correctly
    # rejecting an undated $10M raise and a 404'd Tracxn snippet. Require a date unless it is new to us.
    #
    # Same first-run hole as diff_leadership_hire, fixed the same way (2026-08-24). `not first_run` kept
    # an undated round from firing when there is no baseline to call it new against — correct by default,
    # since an undated 2019 round must not score. But with commit() seeding it unflagged, a genuinely
    # fresh undated round found on run 1 would be `prior.get("round")` from run 2 on and never fire.
    # `newly_disclosed: true` lets the observer open the gate when it has positive evidence the round is
    # new (a filing or announcement it can attribute but not date). Not measured on batch 3/6 — all five
    # funding runs were clean negatives — but the defect is identical, so it is closed the same way
    # rather than left as a known hole in a file being edited anyway.
    undated_but_new = age is None and not prior.get("round") and (
        not first_run or bool(cur.get("newly_disclosed")))

    present = bool(is_newer and (in_window or undated_but_new))
    return {
        "signal": "funding",
        "present": present,
        "recency_days": age,
        "amount": cur.get("amount") if present else None,
        "round": cur.get("round") if present else None,
        "investor": cur.get("investor") if present else None,
        "evidence": (
            "{} dated {} ({}d old)".format(cur.get("round") or "round", cur.get("date"), age)
            if present else
            "observed round is not newer than baseline, or outside {}d".format(limit)
        ),
        "first_run": first_run,
    }


def diff_open_jobs(baseline, obs, today, first_run):
    """Delta = postings not in the baseline. Also reports disappeared roles — a role that vanishes may
    mean the hire happened, which pairs with leadership_hire (see _delta_state.md)."""
    cur = obs.get("open_roles")
    if cur is None:
        return None
    prior_keys = {_role_key(r) for r in (baseline.get("open_roles") or [])}
    cur_keys = {_role_key(r) for r in cur}

    new_roles = [r for r in cur if _role_key(r) not in prior_keys]
    disappeared = [r for r in (baseline.get("open_roles") or []) if _role_key(r) not in cur_keys]

    ages = [a for a in (_age_days(r.get("posted"), today) for r in cur) if a is not None and a >= 0]

    # open_jobs is a current-state signal: a role is open or it is not, so ANY open corporate role is
    # present, not only newly-appeared ones. The delta is reported for the hook, not the gate.
    return {
        "signal": "open_jobs",
        "present": bool(cur),
        "recency_days": min(ages) if ages else None,
        "roles": cur,
        "new_since_last_run": len(new_roles),
        "disappeared_since_last_run": [r.get("title") for r in disappeared],
        "evidence": "{} open role(s), {} new since last run".format(len(cur), len(new_roles)),
        "first_run": first_run,
    }


DIFFERS = {
    "new_location": diff_new_location,
    "leadership_hire": diff_leadership_hire,
    "open_jobs": diff_open_jobs,
    "funding": diff_funding,
}


def compute(domain, observation, today):
    baseline = read_state(domain)
    first_run = not baseline
    signals = {}
    for name, fn in DIFFERS.items():
        result = fn(baseline, observation, today, first_run)
        if result is not None:
            signals[name] = result
    # The summary belongs here, not in the CLI, so every caller sees it. `present` is decided by the
    # diff and the judgement merge never changes it, so this is stable.
    present = sorted(n for n, s in signals.items() if s.get("present"))
    return {
        "domain": normalize_domain(domain),
        "first_run": first_run,
        "baseline_last_run": baseline.get("last_run"),
        "observed_keys": sorted(k for k in observation if k in ("locations", "execs", "funding", "open_roles", "contract_expiry")),
        "signals": signals,
        "present_signals": present,
        # Multi-signal accounts are the high-value case: they are what pushes a score to `high` and the
        # only way `hot_account` (3+ signals inside 30 days) can ever be reached.
        "multi_signal": len(present) >= 2,
    }


def commit(domain, observation, today, signals):
    """Persist today's observation as the next baseline, stamping flagged_run on anything surfaced.

    Only keys the observer actually returned are overwritten. An omitted key keeps its prior value —
    "I didn't look" must not erase what we knew.
    """
    baseline = read_state(domain)
    stamp = today.isoformat()

    if observation.get("locations") is not None:
        loc = dict(observation["locations"])
        loc["sites"] = [_site_name(s) for s in (loc.get("sites") or [])]
        baseline["locations"] = loc

    if observation.get("execs") is not None:
        prior = {_exec_key(p): p for p in (baseline.get("execs") or [])}
        surfaced = {_exec_key({"name": signals.get("leadership_hire", {}).get("person_name") or "",
                               "role": signals.get("leadership_hire", {}).get("role") or ""})}
        merged = []
        for person in observation["execs"]:
            record = dict(person)
            key = _exec_key(person)
            existing_flag = prior.get(key, {}).get("flagged_run")
            if existing_flag:
                record["flagged_run"] = existing_flag
            elif key in surfaced and signals.get("leadership_hire", {}).get("present"):
                record["flagged_run"] = stamp
            merged.append(record)
        baseline["execs"] = merged

    if observation.get("funding") is not None:
        record = dict(observation["funding"]) if observation["funding"] else {}
        prior = baseline.get("funding") or {}
        if record:
            if prior.get("round") == record.get("round") and prior.get("flagged_run"):
                record["flagged_run"] = prior["flagged_run"]
            elif signals.get("funding", {}).get("present"):
                record["flagged_run"] = stamp
        baseline["funding"] = record

    if observation.get("open_roles") is not None:
        baseline["open_roles"] = list(observation["open_roles"])

    if observation.get("contract_expiry") is not None:
        baseline["contract_expiry"] = observation["contract_expiry"]

    baseline["domain"] = normalize_domain(domain)
    baseline["last_run"] = stamp

    os.makedirs(STATE_DIR, exist_ok=True)
    path = _path(domain)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(baseline, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)  # atomic: a crash mid-write must not corrupt the detection memory
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("action", choices=["read", "diff", "commit"])
    ap.add_argument("domain")
    ap.add_argument("--observation", action="append", metavar="FILE",
                    help="observation file (diff/commit). Repeat once per signal — the four s1-* "
                         "subagents each write their own, and a multi-signal account is the point.")
    ap.add_argument("--today", help="override today's date, YYYY-MM-DD (for tests/backfill)")
    args = ap.parse_args()

    today = _today(args.today)

    if args.action == "read":
        print(json.dumps(read_state(args.domain), indent=2, sort_keys=True))
        return

    if not args.observation:
        sys.exit("--observation is required for {}".format(args.action))

    # Each s1-* subagent writes {domain, signal, observation:{...}, judgement:{...}}. Accept one file
    # per signal and merge, because the whole reason for four agents is the multi-signal account: a
    # brief like Portillo's carries new_location + leadership_hire + open_jobs at once, and the score
    # only reaches "high" when they stack.
    observation, judgements = {}, {}
    for path in args.observation:
        with open(path) as fh:
            payload = json.load(fh)
        if not isinstance(payload, dict):
            sys.exit("{}: observation must be a JSON object, got {}".format(path, type(payload).__name__))
        part = payload.get("observation", payload)
        if not isinstance(part, dict):
            sys.exit("{}: 'observation' must be an object".format(path))
        for key, value in part.items():
            if key in observation and observation[key] != value:
                sys.exit(
                    "conflict on '{}': two observation files disagree ({} vs {}). Each signal owns its "
                    "own key — do not have two agents report the same one.".format(path, observation[key], value)
                )
            observation[key] = value
        name = payload.get("signal")
        if payload.get("judgement"):
            if name in judgements:
                sys.exit("{}: two files claim signal '{}'".format(path, name))
            judgements[name] = payload["judgement"]

    result = compute(args.domain, observation, today)

    # Merge the observer's judgement into the signal it belongs to, so the output is ready for
    # score_accounts.py without a separate merge step. The delta decides `present`; the observer's
    # `present` is advisory and is reported as `observer_present` when the two disagree — a disagreement
    # is worth seeing, not silently resolving.
    unmatched = []
    for name, judgement in judgements.items():
        if name not in result["signals"]:
            unmatched.append({
                "signal": name,
                "reason": "no observation key for this signal, so no delta could be computed",
            })
            continue
        sig = result["signals"][name]
        observer_present = judgement.get("present")
        for key, value in judgement.items():
            if key == "present":
                continue
            if key == "recency_days" and value is not None:
                sig[key] = value  # the observer dated the event; the differ could not
            elif key not in sig or sig.get(key) is None:
                sig[key] = value
        if observer_present is not None and bool(observer_present) != bool(sig.get("present")):
            sig["observer_present"] = bool(observer_present)
            sig["note"] = (
                "observer said present={}, baseline diff says {} — the diff wins (a fact already in "
                "the baseline is not a new signal)".format(observer_present, sig.get("present"))
            )
    if unmatched:
        result["unmatched_judgements"] = unmatched

    if args.action == "commit":
        result["baseline_written"] = commit(args.domain, observation, today, result["signals"])

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
