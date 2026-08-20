#!/usr/bin/env python3
"""Match an account to its best conjunctural (industry/macro) signal — the Stage 2 fallback layer for
accounts with a thin or empty Stage 1 signal set. See knowledge/conjunctural/README.md for the concept,
the entry schema, and the hard rules (primary sources only, never populate from memory, facts+cost effects
never advice, quantify-or-fall-back).

WHEN THIS RUNS
    After scoring (score_accounts.py), only for accounts where score < CONJUNCTURAL_THRESHOLD (30) or
    zero Tier-1 signals fired. A well-signalled account never needs this — the account signal always wins.

WHAT IT RETURNS
    The single best-matched, best-quantified, not-expired entry, or None. None is a valid, common result:
    if nothing quantifiable matches the account's state/vertical, the first-touch stays on the vertical-
    pain fallback (knowledge/pains_by_vertical.md) rather than send an unquantified macro cliché — that
    is the rule this script exists to enforce, not just a fallback path.

USAGE
    python3 scripts/conjunctural_match.py --state CA --vertical fsr --persona operations --locations 6
    python3 scripts/conjunctural_match.py --state IL --vertical fast_casual --locations 3 --city Chicago --json

Requires only stdlib.
"""
import argparse
import glob
import json
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER_DIR = os.path.join(HERE, "..", "knowledge", "conjunctural", "register")


def load_register():
    """All entries from every knowledge/conjunctural/register/*.json file. Skips a file that fails to
    parse rather than crashing the whole match — one bad research file shouldn't take down every account.
    """
    entries = []
    for path in sorted(glob.glob(os.path.join(REGISTER_DIR, "*.json"))):
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARNING: skipping unreadable register file {path}: {e}", file=sys.stderr)
            continue
        for e in data.get("entries", []):
            e["_file"] = os.path.basename(path)
            entries.append(e)
    return entries


def not_expired(entry, today):
    review_by = entry.get("review_by")
    if not review_by:
        return True  # no review date set — don't silently drop it, but this should be rare
    try:
        return date.fromisoformat(review_by) >= today
    except ValueError:
        return True


def scope_matches(entry, state, city):
    scope = entry.get("scope") or {}
    level = scope.get("level")
    if level == "federal":
        return True
    if level == "state":
        return bool(state) and scope.get("state", "").upper() == state.upper()
    if level == "city":
        if not city:
            return False
        cities = [c.lower() for c in (scope.get("cities") or [])]
        return city.lower() in cities
    return False


def score_entry(entry, state, city, vertical, persona, locations, today):
    """Higher is better. Returns None if the entry doesn't apply at all."""
    if not not_expired(entry, today):
        return None
    if not scope_matches(entry, state, city):
        return None
    # An explicit EMPTY list is a "never selectable" guard (e.g. LA's fair-workweek entries in
    # scheduling_law.json are retail-only and deliberately carry verticals:[] / personas:[] so they can
    # never be matched to a restaurant account). This must be checked before the vertical/persona filter
    # below: `[] and X` is falsy in Python, so `entry.get("verticals") and ...` would silently SKIP the
    # rejection for an empty list — the opposite of "never match" — bug caught reviewing scheduling_law.json
    # 2026-08-13, where the research agent's own caveats promise this guarantee explicitly.
    if entry.get("verticals") == [] or entry.get("personas") == []:
        return None
    if vertical and entry.get("verticals") and vertical not in entry["verticals"]:
        return None
    if persona and entry.get("personas") and persona not in entry["personas"]:
        return None

    score = 0.0
    scope = entry.get("scope") or {}
    # More specific geography wins: city > state > federal.
    score += {"city": 3, "state": 2, "federal": 1}.get(scope.get("level"), 0)
    # A quantified entry is the whole point (see README's "quantify or fall back" rule) — heavily
    # preferred over an entry that can only ever be supporting context.
    if entry.get("quantification"):
        score += 5
    # status: an in-effect fact beats a scheduled one, which beats a merely proposed one.
    score += {"in_effect": 2, "scheduled": 1, "proposed": 0}.get(entry.get("status"), 0)
    # Vertical/persona specificity — CONTINUOUS, not a <=2 binary cliff (bug caught by the commodity
    # research agent 2026-08-13: beef legitimately spans 3 verticals while eggs/cocoa/dairy span 1-2, so
    # a binary "+1 if <=2" made a broad, well-evidenced beef story lose to a narrower one on a technicality
    # that had nothing to do with which story actually fits the account better). More verticals/personas
    # listed = more of a wildcard = less credit, smoothly, capped so a single-match entry gets the max.
    if vertical and entry.get("verticals"):
        score += 1.5 / len(entry["verticals"])
    if persona and entry.get("personas"):
        score += 1.5 / len(entry["personas"])
    # Small, deliberate tie-break toward "problem" framings — outbound_voice.md's skeleton is pain-led
    # (problem-they'll-nod-at -> we-solve-it), so a cost_up/compliance_burden fact needs less selling into
    # that shape than a cost_down one (a price falling is margin RELIEF, a different, harder-to-open
    # persuasion mechanic — see the eggs entry's own angle, which has to work to reframe good news as a
    # problem). Small on purpose: this is a tie-break, not a veto — a strongly-quantified cost_down entry
    # can and should still win when it's clearly the better-evidenced story.
    score += {"cost_up": 0.3, "compliance_burden": 0.3, "demand_down": 0.2}.get(entry.get("direction"), 0)
    # Prefer a primary source over secondary when everything else ties — see README rule 1.
    if (entry.get("source") or {}).get("primary"):
        score += 0.5
    return score


# Bases that represent a real, measured COST or PRICE movement — the only kind that may open an email.
# Explicit whitelist, not a catch-all: research agents keep inventing precise basis names for things that
# are NOT cost quantifications (the NRA entry's "pct_of_fullservice_operators_citing_insurance_as_a_
# significant_challenge" carries a value of 91 but is a share of OPERATORS, not a premium change — treating
# it as usable would have opened an email on a sentiment statistic). Unknown bases default to "not usable"
# rather than the old behaviour of rendering a raw fallback string and marking it usable — the safer
# failure mode matches the README rule: fall back to vertical pain rather than guess at a claim.
_SENTIMENT_BASIS_MARKERS = ("_citing_", "_operators_", "_reporting_")


def quantify_for_account(entry, locations):
    """Scale the entry's per-unit quantification to this account's footprint. Returns a human string, or
    None if the entry has no usable quantification (in which case it must not be the opener — see README).
    Deliberately simple arithmetic so a rep can double-check it by hand.
    """
    q = entry.get("quantification")
    if not q or q.get("value") is None:
        return None
    basis, value = q.get("basis") or "", q.get("value")
    n = locations or 1

    if any(marker in basis for marker in _SENTIMENT_BASIS_MARKERS):
        return None  # a survey/sentiment stat, not a cost fact about this account — never the opener

    if basis == "per_hourly_employee_per_year":
        return f"~${value:,.0f}/hourly employee/year — no per-site employee count assumed, ask on the call"
    if basis == "per_site_per_year":
        total = value * n
        return f"~${value:,.0f}/site/year → **~${total:,.0f}/year across {n} site(s)**"
    if basis == "pct_of_cogs":
        return f"a {value}% move on an input that is typically a meaningful share of COGS for this vertical"
    if basis == "pct_of_labour":
        return f"a {value}% shift in labour cost structure"
    if basis == "pct_points_fafh_vs_fah_cpi":
        direction = "wider than" if value >= 0 else "narrower than"
        return (f"menu prices running {abs(value):.1f} percentage points {direction} grocery "
                f"prices (CPI food-away-from-home vs food-at-home spread)")
    if basis == "pct_of_delivery_order_value":
        return f"up to {value}% of order value on the fee tier in question — ask which tier they're on"
    if basis.startswith("pct_premium_change"):
        sign = "up" if value >= 0 else "down"
        return f"insurance premiums {sign} {abs(value)}% for the account's segment/line — verify which"

    # Anything else with a real numeric value but no recognized renderer: log-worthy, but conservatively
    # NOT usable as the opener until it's added above and reviewed. See _signal_stack.md-style discipline —
    # a new basis name should be a deliberate addition, not something that silently becomes an email claim.
    return None


def best_match(state, vertical, persona, locations, city=None, today=None):
    today = today or date.today()
    candidates = []
    for e in load_register():
        s = score_entry(e, state, city, vertical, persona, locations, today)
        if s is not None:
            candidates.append((s, e))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    _, entry = candidates[0]

    quant_str = quantify_for_account(entry, locations)
    return {
        "id": entry.get("id"),
        "type": entry.get("type"),
        "title": entry.get("title"),
        "fact": entry.get("fact"),
        "effective_date": entry.get("effective_date"),
        "status": entry.get("status"),
        "angle": entry.get("angle"),
        "proof_pairing": entry.get("proof_pairing"),
        "source_url": (entry.get("source") or {}).get("url"),
        "source_primary": (entry.get("source") or {}).get("primary"),
        "quantified_for_account": quant_str,
        "usable_as_opener": quant_str is not None,  # the README rule, enforced structurally
        "caveats": entry.get("caveats"),
        "_all_candidates_considered": len(candidates),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--state", help="two-letter state code, e.g. CA")
    ap.add_argument("--city", help="city name, for city-level ordinances")
    ap.add_argument("--vertical", choices=["coffee_cafe", "fast_casual", "fsr", "qsr"])
    ap.add_argument("--persona", choices=["csuite", "finance", "founder", "operations"])
    ap.add_argument("--locations", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(REGISTER_DIR) or not glob.glob(os.path.join(REGISTER_DIR, "*.json")):
        sys.exit(f"FATAL: no register files in {REGISTER_DIR} — nothing to match against yet.")

    result = best_match(args.state, args.vertical, args.persona, args.locations, args.city)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if not result:
        print("No conjunctural match — fall back to the vertical-pain default "
              "(knowledge/pains_by_vertical.md).")
        return
    print(f"\n{result['title']}  [{result['id']}]")
    print(f"  fact: {result['fact']}")
    print(f"  effective: {result['effective_date']} ({result['status']})")
    print(f"  quantified: {result['quantified_for_account'] or '— none, DO NOT use as the opener —'}")
    print(f"  usable as opener: {result['usable_as_opener']}")
    print(f"  angle: {result['angle']}")
    if result.get("caveats"):
        print(f"  caveats: {result['caveats']}")
    print(f"  source ({'primary' if result['source_primary'] else 'secondary'}): {result['source_url']}")


if __name__ == "__main__":
    main()
