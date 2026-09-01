#!/usr/bin/env python3
"""Reduce a reactivation bundle to what the analysis step actually reads. Lossy, never silently lossy.

WHY THIS EXISTS
    Measured across 119 bundles: median 15.7 KB, p90 161 KB, max 1.32 MB. `stokesadobe.com` is 866 KB
    (~215k tokens) on its own. An analyst handed the raw file either blows its window or — worse —
    quietly reads the first slice and analyses a truncated deal history as if it were complete, which is
    the exact failure `directives/reactivation_deal_analysis.md` exists to prevent.

    So this does the deterministic pre-slicing, and the analyst does the reasoning. Same split as the
    rest of the pipeline.

TWO RULES THAT SHAPE EVERY CHOICE HERE

    1. **Keep the END of a long transcript, not the beginning.** `reactivation_bundle.py:421` does
       `out[:max_chars]`, hard-truncating 54 of 226 transcripts at exactly 12,000 chars and keeping the
       opening. For closed-lost analysis that is backwards: the objection, the real reason and the next
       step live at the END of a sales call. A 99-minute discovery survives as its first ~13 minutes of
       small talk. This script keeps a small opening slice for context plus a much larger closing slice,
       and says in `_omitted` exactly what it dropped.

    2. **A voicemail is not a conversation.** Gong logs unanswered dial attempts as calls. Anything under
       `SUBSTANTIVE_SEC` collapses to one line — it is noise to be counted, not evidence to be read. The
       directive requires this be stated rather than silently skipped.

USAGE
    python3 scripts/bundle_digest.py <domain> [--budget 60000] [--stdout]

OUTPUT
    output/reactivation/<domain>.digest.json   (gitignored, same as the bundle — real prospect PII)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from gtm_common import normalize_domain  # noqa: E402

BUNDLE_DIR = os.path.join(HERE, "..", "output", "reactivation")
SUBSTANTIVE_SEC = 120          # under this, a "call" is a voicemail or a misdial
DEFAULT_BUDGET = 60000         # total transcript chars kept across all substantive calls
HEAD_SLICE = 1200              # opening context kept when a transcript must be cut
MAX_EMAIL_SUBJECTS = 40


def slice_transcript(text, keep):
    """Keep the tail, plus a short head for context. Returns (text, note_or_None)."""
    if not text:
        return "", None
    if len(text) <= keep:
        return text, None
    if keep <= HEAD_SLICE:
        return text[-keep:], "kept final %d of %d chars" % (keep, len(text))
    head = text[:HEAD_SLICE]
    tail = text[-(keep - HEAD_SLICE):]
    return (head + "\n\n[...MIDDLE CUT — the tail below is where the objection lives...]\n\n" + tail,
            "kept first %d + final %d of %d chars" % (HEAD_SLICE, keep - HEAD_SLICE, len(text)))


def build(domain, budget):
    domain = normalize_domain(domain)
    path = os.path.join(BUNDLE_DIR, domain + ".json")
    if not os.path.exists(path):
        sys.exit("no bundle at %s — run scripts/reactivation_bundle.py %s first" % (path, domain))
    b = json.load(open(path))
    hs = b.get("hubspot") or {}
    calls = (b.get("gong") or {}).get("calls") or []

    substantive = [c for c in calls if (c.get("duration_sec") or 0) >= SUBSTANTIVE_SEC]
    noise = [c for c in calls if (c.get("duration_sec") or 0) < SUBSTANTIVE_SEC]
    # Newest first: the last conversation before it died is the most informative one.
    substantive.sort(key=lambda c: c.get("date") or "", reverse=True)

    per_call = budget // max(1, len(substantive))
    kept_calls, omitted = [], []
    for c in substantive:
        text, note = slice_transcript(c.get("transcript_text") or "", per_call)
        rec = {
            "id": c.get("id"), "title": c.get("title"), "date": c.get("date"),
            "duration_sec": c.get("duration_sec"),
            "duration_min": round((c.get("duration_sec") or 0) / 60.0, 1),
            "external_parties": c.get("external_parties"),
            "trackers_hit": c.get("trackers_hit"),
            "transcript_text": text,
        }
        # A ONE-SIDED transcript is not a conversation, and it is not the same thing as a voicemail.
        # Found on stokesadobe.com's 14.2-minute "Quick Call" (2026-08-05): REP turns = 1, PROSPECT
        # turns = 0 — one unbroken block of rep speech where Gong captured only our side, and whose
        # content names people ("Rita", "Seth") who belong to no contact on this account. Long enough to
        # pass the duration filter, substantive-looking, and worthless as evidence of what the prospect
        # said. Counting rep turns is enough to spot it, so say so rather than let an analyst quote a
        # monologue back to a rep as the prospect's own words.
        rec["prospect_turns"] = text.count("PROSPECT (")
        rec["rep_turns"] = text.count("REP (")
        if rec["prospect_turns"] == 0:
            rec["_one_sided"] = ("NO PROSPECT SPEECH IN THIS TRANSCRIPT — our side only. Do not treat as "
                                "a conversation, do not quote it as the prospect, and check it belongs "
                                "to this account at all.")
        if note:
            rec["_transcript_truncated"] = note
            omitted.append({"call_id": c.get("id"), "title": c.get("title"), "what": note,
                            "retrieve": "python3 -c \"import json;b=json.load(open('output/reactivation/"
                                        "%s.json'));print([c['transcript_text'] for c in "
                                        "b['gong']['calls'] if c['id']=='%s'][0])\""
                                        % (domain, c.get("id"))})
        kept_calls.append(rec)

    emails = hs.get("logged_emails") or []
    by_month = {}
    for e in emails:
        ts = (e.get("hs_timestamp") or e.get("hs_createdate") or "")[:7]
        by_month[ts] = by_month.get(ts, 0) + 1

    digest = {
        "domain": domain,
        "generated_from": b.get("generated"),
        "_digest_note": (
            "Pre-sliced from the raw bundle. %d of %d Gong calls were substantive (>=%ds); the other %d "
            "are voicemails/misdials, counted below but not transcribed. Transcripts keep the TAIL, "
            "because that is where the objection and the next step live." % (
                len(substantive), len(calls), SUBSTANTIVE_SEC, len(noise))),
        "warnings": b.get("warnings") or [],       # verbatim, never summarised
        "company": {"id": hs.get("company_id"), "name": hs.get("company_name")},
        "deals": hs.get("deals") or [],            # small and load-bearing — kept whole
        "contacts": hs.get("contacts") or [],
        "call_summary": {
            "confirmed_total": len(calls),
            "substantive": len(substantive),
            "voicemail_or_misdial": len(noise),
            # already a count in the bundle, not a list — the title-match funnel before confirmation
            "candidates_by_title": (b.get("gong") or {}).get("candidate_calls_by_title"),
            "noise_calls": [{"id": c.get("id"), "title": c.get("title"),
                             "duration_sec": c.get("duration_sec"), "date": c.get("date")}
                            for c in noise],
        },
        "calls": kept_calls,
        "email_summary": {
            "total": len(emails),
            "by_month": [{"month": k, "count": v} for k, v in sorted(by_month.items()) if k],
            "subjects": [{"date": (e.get("hs_timestamp") or "")[:10],
                          "direction": e.get("hs_email_direction"),
                          "status": e.get("hs_email_status"),
                          "subject": e.get("hs_email_subject")}
                         for e in emails[:MAX_EMAIL_SUBJECTS]],
        },
        "_omitted": omitted or None,
    }
    return digest


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("domain")
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help="total transcript chars kept across substantive calls (default %d)" % DEFAULT_BUDGET)
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the file")
    a = ap.parse_args()

    d = build(a.domain, a.budget)
    if a.stdout:
        print(json.dumps(d, indent=2))
        return 0
    out = os.path.join(BUNDLE_DIR, d["domain"] + ".digest.json")
    with open(out, "w") as fh:
        json.dump(d, fh, indent=2)
    raw = os.path.getsize(os.path.join(BUNDLE_DIR, d["domain"] + ".json"))
    new = os.path.getsize(out)
    print("%-24s %7.1f KB -> %6.1f KB  (%.1fx)  calls %d substantive / %d noise%s" % (
        d["domain"], raw / 1024.0, new / 1024.0, raw / float(new or 1),
        d["call_summary"]["substantive"], d["call_summary"]["voicemail_or_misdial"],
        "  [%d truncated]" % len(d["_omitted"]) if d["_omitted"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
