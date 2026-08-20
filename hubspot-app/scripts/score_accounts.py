#!/usr/bin/env python3
"""Score accounts from Stage-1 signal verdicts — the ga_score_aggregator formula as code.

Input:  a JSON file: [{"company","domain","rep_email","vertical","persona","locations",
                       "signals":{new_location:{...},leadership_hire:{...},open_jobs:{...},funding:{...}},
                       "motion":"reactivation"}]      <- optional; omit for normal Tier-1 accounts
Output: the same list + score, score_band, status, hot_account, cadence_template, suite — printed as JSON.

`motion: "reactivation"` maps the account to the **UKI Reactivation** flow (assumed name) instead of a vertical × persona
cell (see cadences/UKI_FLOWS.md — reactivation sits outside the 4×4 matrix). vertical/persona are still
required and still classified: they aim the first-touch angle, they just don't pick the flow.

Formula (agents/stage1_signals/ga_score_aggregator.md, defined 2026-08-10):
    contribution = (strength/5) × weight × confidence_mult × recency_mult   (0 if present:false)
    raw   = Σ contributions
    base  = min(100, raw / 3.5 × 100)
    score = min(100, round(base × segment_mult))                (+ce_boost when CRM has contract expiry)
    all-low-confidence guard: cap at 59.

RECENCY MODEL (recalibrated 2026-08-12 after the first 80 real accounts):
Recency now *discounts* a signal instead of gating it. Measured across batch 2 + reactivation batch 1/6,
`new_location` was 88% of all detections, `funding` fired 0/80 and `leadership_hire` 1/80 — not because
those events don't happen, but because real ones kept landing just outside a hard window (Goode Partners
PE at 252d, DIAFA at 324d, Insomnia's CFO + buyout at ~14mo) or came from sources that never published a
date, which made agents score them `present:false` and throw real intel away.

So: each signal has an outer WINDOW beyond which it genuinely doesn't count, and inside that window the
contribution decays by age. An undated-but-corroborated event is counted with a small haircut rather than
discarded — recording "we found it, we couldn't date it" beats pretending we found nothing.
"""
import json
import sys

WEIGHTS = {"new_location": 3.0, "leadership_hire": 2.0, "open_jobs": 1.5, "funding": 1.0}
CONF_MULT = {"high": 1.0, "med": 0.8, "medium": 0.8, "low": 0.5}

# Outer bound per signal, in days. Past this the signal is not a "why now" at all and scores 0.
# leadership_hire is deliberately tighter: a 10-month-old hire has stopped being news.
# open_jobs is a current-state signal (a role is open or it isn't), so it has no window.
WINDOWS = {"new_location": 365, "leadership_hire": 180, "funding": 365, "open_jobs": None}

# Age discount inside the window. Was a hard gate before 2026-08-12.
RECENCY_TIERS = ((90, 1.0), (180, 0.8), (270, 0.6), (365, 0.4))
UNDATED_MULT = 0.85  # verified event, no publishable date — discount, don't discard

# Below this score (or with zero present signals), the first touch should try the conjunctural
# (industry/macro) layer before falling back to the generic vertical-pain angle. See
# knowledge/conjunctural/README.md + scripts/conjunctural_match.py. Set here, not in the pipeline, so
# score_accounts.py is the single place that decides "this account has nothing account-specific to say".
CONJUNCTURAL_THRESHOLD = 30

VERTICAL_LABEL = {"coffee_cafe": "Coffee & Cafe", "fast_casual": "Fast Casual", "fsr": "FSR", "qsr": "QSR"}
PERSONA_LABEL = {"csuite": "C-Suite", "finance": "Finance", "founder": "Founder", "operations": "Operations"}
SUITE = {"csuite": "Full Suite", "founder": "Full Suite", "finance": "IM", "operations": "IM"}
REACTIVATION_FLOW = "UKI Reactivation"  # assumed name — confirm in cadences/UKI_FLOWS.md


def segment_mult(locations):
    if locations is None:
        return 0.8
    if locations >= 30:
        return 1.0
    if locations >= 10:
        return 0.95
    if locations >= 2:
        return 0.8
    return 0.3


def band(score):
    return "high" if score >= 75 else "medium" if score >= 60 else "low" if score >= 40 else "thin"


def recency_mult(name, recency_days):
    """Age discount for one signal. Returns 0.0 when the event is outside the signal's window.

    recency_days is None for a corroborated event whose date no source published — common in this
    segment (small US operators rarely get dated coverage, and ATS/press pages often omit dates).
    """
    window = WINDOWS.get(name)
    if recency_days is None:
        return UNDATED_MULT
    if recency_days < 0:
        return 0.0  # a future-dated event is a data error, not a signal
    if window is not None and recency_days > window:
        return 0.0
    for limit, mult in RECENCY_TIERS:
        if recency_days <= limit:
            return mult
    return 0.0


def score_account(acct):
    signals = acct.get("signals", {})
    raw, confidences, recent = 0.0, [], 0
    for name, sig in signals.items():
        if not sig or not sig.get("present"):
            continue
        rd = sig.get("recency_days")
        rmult = recency_mult(name, rd)
        if rmult == 0.0:
            # Real, but not a why-now. Recorded on the signal so the brief can still reference it as
            # context (see directives/signals/*.md "out of window" rule).
            sig["scored"] = False
            sig["scored_reason"] = (
                f"future-dated ({rd}d) — check the source date" if rd is not None and rd < 0
                else f"outside the {WINDOWS.get(name)}-day window ({rd}d)"
            )
            continue
        strength = min(5, max(0, sig.get("strength") or 0))
        conf = (sig.get("confidence") or "low").lower()
        contribution = (strength / 5.0) * WEIGHTS.get(name, 1.0) * CONF_MULT.get(conf, 0.5) * rmult
        raw += contribution
        sig["scored"] = True
        sig["recency_mult"] = rmult
        confidences.append(conf)
        if rd is not None and rd <= 30:
            recent += 1
    base = min(100.0, raw / 3.5 * 100.0)  # recalibrated 2026-08-11 on first real batch (was /6) — see ga_score_aggregator.md
    score = min(100, round(base * segment_mult(acct.get("locations"))))
    if confidences and all(c == "low" for c in confidences):
        score = min(score, 59)  # a rumour never makes an account "ready to launch"
    acct["score"] = score
    acct["score_band"] = band(score)
    acct["status"] = "ready" if score >= 60 else "scored"
    acct["hot_account"] = recent >= 3
    # Nothing account-specific to hook the first touch on — try knowledge/conjunctural before falling
    # back to the generic vertical-pain default. `any(...present...)` catches the case where a signal
    # fired but scored 0 raw contribution (shouldn't happen, kept as a defensive OR on the score check).
    acct["needs_conjunctural"] = score < CONJUNCTURAL_THRESHOLD or not any(
        s and s.get("present") for s in signals.values()
    )
    v, p = acct["vertical"], acct["persona"]
    acct["suite"] = SUITE[p]
    if acct.get("motion") == "reactivation":
        acct["cadence_template"] = REACTIVATION_FLOW
    else:
        acct["cadence_template"] = f"{VERTICAL_LABEL[v]} × {PERSONA_LABEL[p]} ({SUITE[p]} · Tier 1)"
    return acct


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 score_accounts.py stage1_results.json")
    with open(sys.argv[1]) as f:
        accounts = json.load(f)
    print(json.dumps([score_account(a) for a in accounts], indent=2))


if __name__ == "__main__":
    main()
