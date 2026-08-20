#!/usr/bin/env python3
"""Open-roles probe for the `open_jobs` Tier-1 signal — the L2 augment (directives/signals/open_jobs.md).

WHY THIS EXISTS
    Measured on the first 80 real accounts, `open_jobs` fired 5/80 (6%). The named cause was the
    "ATS wall": careers pages that hand off to Paycor / Lever / iCIMS / Workday / ADP / Paylocity /
    Poached, which a plain WebFetch cannot read. Agents correctly recorded "unverifiable — not counted
    rather than fabricated", so real corporate hiring went undetected.

HOW IT SOLVES IT (tiered — cheapest and most authoritative first)
    T1  Detect the ATS from the company's own careers page (plain fetch), then call that ATS's PUBLIC
        JSON API. Free, no scraper, company-scoped by construction, and it carries real post dates.
        Covers Greenhouse · Lever · Ashby · Workable · Recruitee · SmartRecruiters · Personio · Teamtailor.
    T1b If BOTH the careers-page fetch above AND the fetch-free token probe (below) find nothing: one
        Firecrawl shot (FIRECRAWL_API_KEY, premium plan) at <domain>/careers before falling to Apify.
        Added 2026-08-14, confirmed live against insomniacookies.com/careers — one of this docstring's
        own named 403 failures below: plain fetch still 403s, Firecrawl reads it cleanly and reveals the
        Lever token directly. Deliberately ONE request on ONE path, not a retry wired into every path the
        careers-page detector tries — an earlier version did that and cost up to 22 Firecrawl credits and
        60+ seconds on a single company, almost all of it burned on paths that don't exist. See
        detect_ats_via_firecrawl()'s docstring.
    T2  For boards with no public JSON (Workday, iCIMS, Paycor, Paylocity, ADP, Poached), fall back to
        Apify. This is where Apify actually earns its cost — not on aggregator search.

WHAT IT DELIBERATELY DOES NOT DO
    Search a job aggregator by company name. Tested and rejected 2026-08-12: an Indeed name-search for
    "Giordano's" returned a State Farm agent named Charles Giordano, Giordano's Recycling, Giordano's
    Heating & Air, and a *different franchisee* ("Giordanos of Fort Wayne"). Aggregator company matching
    is too noisy to score from, and franchisee confusion is the exact trap `new_location.md` already warns
    about. Company-scoped ATS boards avoid both by construction.

    It also does not touch LinkedIn. Public job postings are less fraught than profile data, but scraping
    either breaches LinkedIn's ToS, and the repo rule is explicit (`_signal_stack.md`: no raw LinkedIn
    scraping). LinkedIn postings are usually mirrors of the same ATS this script reads directly.

CORPORATE vs UNIT-LEVEL
    `open_jobs` is an ABOVE-STORE signal by design: a crew/barista/line-cook req says nothing about a
    systems gap. This script splits them and reports both, because unit-level hiring is still useful —
    a full FOH/BOH slate in a new metro corroborates `new_location` (see that playbook's stage rule).
    Only corporate roles drive the `open_jobs` score.

USAGE
    python3 scripts/jobs_probe.py <domain> [--company "Name"] [--json] [--apify] [--max N]
        --apify   allow the T2 Apify fallback (costs money; off by default)
        --json    emit only the canonical signal object, for a pipeline to consume
Requires only stdlib (urllib, not the firecrawl SDK/CLI — same direct-REST pattern as gong_pull.py /
upsert_brief.py). Reads APIFY_TOKEN from the repo-root .env when --apify is used, and FIRECRAWL_API_KEY
whenever present (no flag needed — T1b only fires once both free tiers have already failed, so it's a
no-op, not an extra cost, on the majority of companies where a free tier already works).
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
TIMEOUT = 30


def _load_dotenv():
    path = os.path.join(HERE, "..", ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


# --------------------------------------------------------------------------- classification
# Above-store roles that imply a systems/cost-control gap. This is the signal.
CORPORATE_RE = re.compile(
    r"\b(financ\w*|accounting|accountant|controller|fp&a|payroll|treasur\w*|audit\w*|"
    r"procure\w*|purchasing|supply\s*chain|inventory|category\s*manager|"
    r"operations?|ops|systems?|information\s*technolog\w*|\bit\b|technolog\w*|"
    r"data|analytics?|analyst|business\s*intelligence|\bbi\b|engineer\w*|developer|"
    r"revenue|pricing|strateg\w*|transformation|continuous\s*improvement)\b", re.I)

# Unambiguous IN-RESTAURANT job titles. These beat everything, however senior they sound — a General
# Manager or Executive Chef runs a room, not the group's systems.
UNIT_TITLE_RE = re.compile(
    r"\b(store\s*manager|general\s*manager|\bagm\b|\bgm\b|assistant\s*general\s*manager|"
    r"restaurant\s*manager|kitchen\s*manager|bakery\s*manager|cafe\s*manager|"
    r"store\s*operations\s*manager|department\s*manager|assistant\s*manager|"
    r"shift\s*(lead|leader|supervisor|manager)|executive\s*chef|sous\s*chef|head\s*chef|"
    r"pastry\s*chef|chef\s*de\s*partie|team\s*lead(er)?)\b", re.I)

# Hourly / in-restaurant role words. A corporate or senior marker OVERRIDES these, because titles like
# "IT Security Analyst", "Head of Delivery & Digital" and "Manager, Kitchen Systems" are above-store.
UNIT_WORD_RE = re.compile(
    r"\b(crew|team\s*member|barista|baker|bakery\s*associate|cook|dishwash\w*|cashier|"
    r"server|waiter|waitress|host|hostess|busser|bartender|barback|runner|"
    r"delivery|driver|courier|kitchen|culinary|valet|janitor|porter|security|"
    r"catering\s*(assistant|associate)|line\s*server|food\s*prep|prep)\b", re.I)

# Seniority for strength banding.
SENIOR_RE = re.compile(
    r"\b(chief|c\.?[eofit]\.?o\.?|president|vp\b|vice\s*president|head\s*of|"
    r"director|senior\s*director|sr\.?\s*director|principal)\b", re.I)

# Above-store but narrow remit — real, just weaker. Doesn't drive the open_jobs score.
NARROW_RE = re.compile(r"\b(marketing|brand|social|creative|recruit\w*|talent|"
                       r"human\s*resources|\bhr\b|people|legal|counsel|training|"
                       r"communications?|\bpr\b|design)\b", re.I)


def classify(title):
    """-> 'corporate' | 'unit' | 'narrow' | 'other'.

    Precedence matters and was corrected 2026-08-12: an explicit in-restaurant TITLE always wins, but a
    corporate/senior marker beats a mere in-restaurant WORD. Without that split, "IT Security Analyst"
    and "Manager, Kitchen Systems" were being discarded as unit-level.
    """
    t = title or ""
    if UNIT_TITLE_RE.search(t):
        return "unit"
    corporate = bool(CORPORATE_RE.search(t))
    senior = bool(SENIOR_RE.search(t))
    if UNIT_WORD_RE.search(t) and not (corporate or senior):
        return "unit"
    if corporate:
        return "corporate"
    if NARROW_RE.search(t):
        return "narrow"
    if senior:
        return "corporate"          # "VP, Guest Experience" — above-store even if the function is odd
    return "other"


# --------------------------------------------------------------------------- http
def fetch(url, as_json=True, data=None, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json,text/html;q=0.8"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h,
                                method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
        return json.loads(raw) if as_json else raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return {"_err": e.code} if as_json else ""
    except Exception as e:                                   # noqa: BLE001 - network is best-effort
        return {"_err": type(e).__name__} if as_json else ""


# --------------------------------------------------------------------------- Firecrawl (optional retry)
FIRECRAWL_API = "https://api.firecrawl.dev/v2/scrape"


def fetch_via_firecrawl(url):
    """Retry a URL through Firecrawl when the plain fetch() above came back empty/blocked.

    Only for the careers-page fetch in detect_ats_from_careers() — the documented failure mode is
    403/Cloudflare and JS-rendered pages with no ATS string in the raw HTML (see module docstring and
    _signal_stack.md). Returns markdown text, or None if FIRECRAWL_API_KEY isn't set or the call fails —
    same silent-degrade contract as fetch(), never raises.
    """
    token = os.environ.get("FIRECRAWL_API_KEY")
    if not token:
        return None
    body = json.dumps({"url": url, "formats": ["markdown"]}).encode()
    req = urllib.request.Request(FIRECRAWL_API, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.loads(r.read())
    except Exception:                                          # noqa: BLE001 - best-effort, like fetch()
        return None
    if not d.get("success"):
        return None
    return (d.get("data") or {}).get("markdown")


# --------------------------------------------------------------------------- ATS detection
# token-bearing fingerprints found on a company's own careers page
ATS_PATTERNS = [
    ("greenhouse", r"(?:job-)?boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-z0-9_-]+)"),
    ("lever", r"jobs\.lever\.co/([a-z0-9_-]+)"),
    ("ashby", r"jobs\.ashbyhq\.com/([a-z0-9_.-]+)"),
    ("workable", r"apply\.workable\.com/([a-z0-9_-]+)"),
    ("recruitee", r"([a-z0-9_-]+)\.recruitee\.com"),
    ("smartrecruiters", r"careers\.smartrecruiters\.com/([a-zA-Z0-9_-]+)"),
    ("personio", r"([a-z0-9_-]+)\.jobs\.personio\.(?:de|com)"),
    ("teamtailor", r"([a-z0-9_-]+)\.teamtailor\.com"),
    # T2 — no public JSON API; needs Apify
    ("workday", r"([a-z0-9_-]+)\.(?:wd\d+\.)?myworkdayjobs\.com"),
    ("icims", r"([a-z0-9_-]+)\.icims\.com"),
    ("paylocity", r"recruiting\.paylocity\.com/[Rr]ecruiting/[Jj]obs/[A-Za-z]+/([a-z0-9-]+)"),
    ("paycor", r"(?:secure|recruiting)\.paycor\.com[^\"'\s]*"),
    ("paycom", r"([a-z0-9_-]+)\.paycomonline\.net"),
    ("adp", r"(?:recruiting|workforcenow)\.adp\.com[^\"'\s]*"),
    ("poached", r"poachedjobs\.com/[^\"'\s]*"),
    ("culinaryagents", r"culinaryagents\.com/[^\"'\s]*"),
]
JSON_API_VENDORS = {"greenhouse", "lever", "ashby", "workable", "recruitee",
                    "smartrecruiters", "personio", "teamtailor"}

CAREERS_PATHS = ["/careers", "/careers/", "/jobs", "/jobs/", "/join-us", "/work-with-us",
                 "/employment", "/careers/open-positions", "/about/careers", "/company/careers", "/"]


def detect_ats_from_careers(domain):
    """Fingerprint the ATS from the company's own careers page, via a plain (free) fetch only.

    Frequently impossible: measured 2026-08-12, insomniacookies.com and portillos.com both return 403
    (Cloudflare) and sweetgreen.com renders its board in JS with no ATS string in the HTML. So this is
    an opportunistic first try, never the only path — see probe_ats_tokens() for the fetch-free fallback,
    and detect_ats_via_firecrawl() for the paid last-resort retry (main() calls it only if both of those
    free paths come up empty — see that function's docstring for why it's not wired in here directly).
    """
    for path in CAREERS_PATHS:
        for scheme in ("https://", "https://www."):
            html = fetch(f"{scheme}{domain}{path}", as_json=False)
            if not html or len(html) < 200:
                continue
            for vendor, pat in ATS_PATTERNS:
                m = re.search(pat, html, re.I)
                if m:
                    return vendor, (m.group(1) if m.groups() else None), f"{scheme}{domain}{path}"
            break
    return None, None, None


def detect_ats_via_firecrawl(domain):
    """Last-resort careers-page fetch through Firecrawl (FIRECRAWL_API_KEY, premium plan) — ONE request
    against the single most common path, not a retry of every path detect_ats_from_careers() tried.

    Deliberately NOT inlined into detect_ats_from_careers()'s per-path loop: that loop tries up to 11
    paths x 2 schemes, and retrying every failure through Firecrawl there cost up to 22 credits and took
    over 60s per company on first try (2026-08-14) — most of it burned on paths that don't even exist.
    A company's careers page is overwhelmingly at /careers when it exists at all, so one shot there
    covers the documented failure mode (403/Cloudflare, JS-rendered board) for a single credit. Confirmed
    live 2026-08-14: insomniacookies.com/careers 403s on a plain fetch, Firecrawl reads it cleanly and
    reveals the Lever token.

    Only called from main() after BOTH free paths (careers-page plain fetch, ATS token probe) fail —
    see the tier ordering there. Returns (vendor, token, url) or (None, None, None).
    """
    url = f"https://{domain}/careers"
    html = fetch_via_firecrawl(url)
    if not html or len(html) < 200:
        return None, None, None
    for vendor, pat in ATS_PATTERNS:
        m = re.search(pat, html, re.I)
        if m:
            return vendor, (m.group(1) if m.groups() else None), url
    return None, None, None


STOP_SUFFIX = re.compile(r"(group|holdings?|inc|llc|corp|company|co|restaurants?|hospitality|"
                         r"concepts?|brands?|enterprises?)$", re.I)


def token_candidates(domain, company):
    """Plausible ATS board tokens, most likely first. These APIs are free, so trying a few is cheap."""
    root = domain.split(".")[0]
    slug = re.sub(r"[^a-z0-9]+", "", (company or "").lower())
    hyph = re.sub(r"[^a-z0-9]+", "-", (company or "").lower()).strip("-")
    cands = [root, slug, hyph]
    for base in (root, slug):
        trimmed = STOP_SUFFIX.sub("", base)
        if trimmed and trimmed != base and len(trimmed) > 3:
            cands.append(trimmed)
    out, seen = [], set()
    for c in cands:
        if c and len(c) > 2 and c not in seen:
            seen.add(c)
            out.append(c)
    return out[:4]


def probe_ats_tokens(domain, company, verbose=False):
    """Ask each free ATS API whether it hosts a board for this company. No company-site fetch needed,
    so Cloudflare on their marketing site is irrelevant. Returns (vendor, token, roles, board)."""
    for token in token_candidates(domain, company):
        for vendor in ("lever", "greenhouse", "ashby", "workable", "smartrecruiters",
                       "recruitee", "teamtailor"):
            roles, board = roles_from_ats(vendor, token)
            if roles:
                return vendor, token, roles, board
            if verbose:
                print(f"    probe miss: {vendor}/{token}", file=sys.stderr)
    return None, None, [], None


# --------------------------------------------------------------------------- T1: public ATS JSON APIs
def _ms_to_days(ms):
    if not ms:
        return None
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return None
    if ms < 10_000_000_000:          # seconds, not ms
        ms *= 1000
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - dt).days)


def _iso_to_days(s):
    if not s:
        return None
    s = str(s).replace("Z", "+00:00")
    for cut in (s, s[:19] + "+00:00", s[:10]):
        try:
            dt = datetime.fromisoformat(cut)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0, (datetime.now(timezone.utc) - dt).days)
        except ValueError:
            continue
    return None


def roles_from_ats(vendor, token):
    """-> (roles, board_url). roles = [{title, location, age_days, url}]. [] means board empty/unreadable."""
    roles, board = [], None
    if vendor == "greenhouse":
        board = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        d = fetch(board)
        for j in (d or {}).get("jobs", []) if isinstance(d, dict) else []:
            roles.append({"title": j.get("title"),
                          "location": (j.get("location") or {}).get("name"),
                          "age_days": _iso_to_days(j.get("updated_at") or j.get("first_published")),
                          "url": j.get("absolute_url")})
    elif vendor == "lever":
        board = f"https://api.lever.co/v0/postings/{token}?mode=json"
        d = fetch(board)
        for j in d if isinstance(d, list) else []:
            roles.append({"title": j.get("text"),
                          "location": (j.get("categories") or {}).get("location"),
                          "age_days": _ms_to_days(j.get("createdAt")),
                          "url": j.get("hostedUrl")})
    elif vendor == "ashby":
        board = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
        d = fetch(board)
        for j in (d or {}).get("jobs", []) if isinstance(d, dict) else []:
            roles.append({"title": j.get("title"), "location": j.get("location"),
                          "age_days": _iso_to_days(j.get("publishedAt")),
                          "url": j.get("jobUrl")})
    elif vendor == "workable":
        board = f"https://apply.workable.com/api/v1/widget/accounts/{token}?details=true"
        d = fetch(board)
        for j in (d or {}).get("jobs", []) if isinstance(d, dict) else []:
            roles.append({"title": j.get("title"), "location": j.get("location"),
                          "age_days": _iso_to_days(j.get("published_on")),
                          "url": j.get("url") or j.get("shortlink")})
    elif vendor == "recruitee":
        board = f"https://{token}.recruitee.com/api/offers/"
        d = fetch(board)
        for j in (d or {}).get("offers", []) if isinstance(d, dict) else []:
            roles.append({"title": j.get("title"), "location": j.get("location"),
                          "age_days": _iso_to_days(j.get("published_at")),
                          "url": j.get("careers_url")})
    elif vendor == "smartrecruiters":
        board = f"https://api.smartrecruiters.com/v1/companies/{token}/postings?limit=100"
        d = fetch(board)
        for j in (d or {}).get("content", []) if isinstance(d, dict) else []:
            loc = j.get("location") or {}
            roles.append({"title": j.get("name"),
                          "location": ", ".join(x for x in [loc.get("city"), loc.get("region")] if x),
                          "age_days": _iso_to_days(j.get("releasedDate")),
                          "url": (j.get("ref") or {}).get("jobAd")})
    elif vendor == "personio":
        board = f"https://{token}.jobs.personio.de/search.json"
        d = fetch(board)
        for j in d if isinstance(d, list) else []:
            roles.append({"title": j.get("name"), "location": j.get("office"),
                          "age_days": _iso_to_days(j.get("createdAt")), "url": j.get("url")})
    elif vendor == "teamtailor":
        board = f"https://{token}.teamtailor.com/jobs.json"
        d = fetch(board)
        for j in (d or {}).get("jobs", []) if isinstance(d, dict) else []:
            roles.append({"title": j.get("title"), "location": j.get("location"),
                          "age_days": _iso_to_days(j.get("created_at")), "url": j.get("url")})
    return [r for r in roles if r.get("title")], board


# --------------------------------------------------------------------------- T2: Apify fallback
APIFY_ACTOR = "misceres~indeed-scraper"


def roles_from_apify(company, board_hint, max_items=60):
    """Last resort for boards with no public JSON (Workday/iCIMS/Paycor/Paylocity/ADP/Poached).

    Scoped by the ATS board URL when we have one — NOT by company-name search, which is too noisy
    to score from (see the module docstring). Returns (roles, note).
    """
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        return [], "APIFY_TOKEN not set — cannot run the T2 fallback"
    if not board_hint:
        return [], ("no board URL to scope the scrape; refusing a company-name aggregator search "
                    "(too noisy — see jobs_probe.py docstring)")
    body = {"startUrls": [{"url": board_hint}], "maxItems": max_items,
            "saveOnlyUniqueItems": True, "parseCompanyDetails": False}
    url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            items = json.load(r)
    except Exception as e:                                   # noqa: BLE001
        return [], f"Apify run failed: {type(e).__name__}"
    if items and isinstance(items[0], dict) and items[0].get("error"):
        return [], f"Apify actor error: {items[0].get('errorDescription')}"
    roles = []
    for it in items:
        if not isinstance(it, dict) or not it.get("positionName"):
            continue
        roles.append({"title": it.get("positionName"), "location": it.get("location"),
                      "age_days": _iso_to_days(it.get("postingDateParsed")),
                      "url": it.get("url"), "company_seen": it.get("company")})
    return roles, None


# --------------------------------------------------------------------------- signal assembly
def build_signal(domain, company, roles, vendor, board, notes):
    corp = [r for r in roles if classify(r["title"]) == "corporate"]
    narrow = [r for r in roles if classify(r["title"]) == "narrow"]
    unit = [r for r in roles if classify(r["title"]) == "unit"]

    # dedup corporate roles by title+location (agency reposts inflate counts — open_jobs.md)
    seen, corp_ded = set(), []
    for r in sorted(corp, key=lambda x: (x["age_days"] is None, x["age_days"] or 0)):
        k = (str(r["title"]).lower().strip(), str(r.get("location") or "").lower().strip())
        if k in seen:
            continue
        seen.add(k)
        corp_ded.append(r)

    senior = [r for r in corp_ded if SENIOR_RE.search(r["title"] or "")]
    ages = [r["age_days"] for r in corp_ded if r["age_days"] is not None]
    recency = min(ages) if ages else None

    n = len(corp_ded)
    if n == 0:
        strength = 0
    elif n >= 3:
        strength = 5
    elif n == 2:
        strength = 4
    elif senior:
        strength = 3
    else:
        strength = 2

    if vendor in JSON_API_VENDORS:
        confidence = "high"           # the company's own board, read from its official API
    elif vendor:
        confidence = "med"
    else:
        confidence = "low"

    hook = ""
    if senior:
        hook = (f"hiring a '{senior[0]['title']}'"
                + (f" — one of {n} open above-store roles" if n > 1 else " on the corporate board"))
    elif corp_ded:
        hook = f"hiring a '{corp_ded[0]['title']}'" + (f" — {n} open above-store roles" if n > 1 else "")

    sig = {
        "signal": "open_jobs",
        "present": n > 0,
        "strength": strength,
        "recency_days": recency,
        "confidence": confidence,
        "hook_detail": hook,
        "evidence": (f"{vendor or 'no ATS detected'} board"
                     + (f" ({board})" if board else "")
                     + f": {n} above-store role(s), {len(unit)} unit-level, {len(narrow)} narrow-remit"),
        "roles": [{"title": r["title"], "location": r.get("location"),
                   "age_days": r.get("age_days"), "url": r.get("url")} for r in corp_ded[:12]],
        # not part of open_jobs scoring — corroborates new_location's stage (see that playbook)
        "unit_level_count": len(unit),
        "unit_level_locations": sorted({str(r.get("location")) for r in unit if r.get("location")})[:12],
        "ats_vendor": vendor,
        "source_url": board,
    }
    if not sig["present"]:
        sig["note"] = (f"{vendor or 'no ATS'} board read successfully; no above-store ops/finance/IT "
                       f"role open ({len(unit)} unit-level roles found — expected for a small operator)"
                       if roles else (notes or "board unreadable and no fallback available"))
    if notes:
        sig["probe_note"] = notes
    return sig


def main():
    ap = argparse.ArgumentParser(description="Probe a company's real job board for the open_jobs signal.")
    ap.add_argument("domain")
    ap.add_argument("--company", default=None)
    ap.add_argument("--apify", action="store_true", help="allow the paid T2 fallback")
    ap.add_argument("--max", type=int, default=60)
    ap.add_argument("--json", action="store_true", help="print only the signal object")
    args = ap.parse_args()
    _load_dotenv()

    domain = args.domain.replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
    company = args.company or domain.split(".")[0]

    notes, roles, board, tier = None, [], None, "none"

    # 1. Opportunistic: the company's own careers page names its ATS (exact token, but often 403/JS).
    vendor, token, careers_url = detect_ats_from_careers(domain)
    if vendor in JSON_API_VENDORS and token:
        roles, board = roles_from_ats(vendor, token)
        tier = "T1 public API (from careers page)"
        if not roles:
            notes = f"{vendor} board found on the careers page (token {token}) but it returned no postings"

    # 2. Primary in practice: ask the free ATS APIs directly. Works through Cloudflare because we
    #    never touch the company's site.
    if not roles:
        pv, pt, roles, board = probe_ats_tokens(domain, company)
        if roles:
            vendor, token, tier = pv, pt, "T1 public API (token probe)"
            notes = None

    # 3. Both free paths failed — one paid Firecrawl shot at the careers page before Apify. Cheap (1
    #    credit) and often decisive (confirmed on insomniacookies.com 2026-08-12's own 403 case), so try
    #    it before the costlier/noisier Apify fallback rather than after.
    if not roles and not vendor:
        vendor, token, careers_url = detect_ats_via_firecrawl(domain)
        if vendor in JSON_API_VENDORS and token:
            roles, board = roles_from_ats(vendor, token)
            tier = "T1 public API (via Firecrawl careers-page retry)"
            if not roles:
                notes = f"{vendor} board found via Firecrawl (token {token}) but it returned no postings"

    # 4. Hostile board with no public JSON — this is where Apify earns its cost.
    if not roles:
        if vendor and vendor not in JSON_API_VENDORS:
            notes = f"{vendor} board detected — no public JSON API"
            if args.apify:
                roles, err = roles_from_apify(company, careers_url, args.max)
                board, tier = careers_url, "T2 Apify scrape"
                if err:
                    notes += f"; {err}"
            else:
                notes += " (re-run with --apify to scrape it)"
        elif not vendor:
            fc = "tried" if os.environ.get("FIRECRAWL_API_KEY") else "not configured — set FIRECRAWL_API_KEY"
            notes = (f"no board found: careers page unreachable (plain fetch + Firecrawl {fc}) or "
                     "genuinely has no ATS fingerprint, and no free ATS API hosts a board "
                     f"under the tokens tried ({', '.join(token_candidates(domain, company))})")

    sig = build_signal(domain, company, roles, vendor, board or careers_url, notes)

    if args.json:
        print(json.dumps(sig, indent=2))
        return

    print(f"\n{company}  ({domain})")
    print(f"  ATS: {vendor or '—'}{f' [{token}]' if token else ''}   tier: {tier}")
    print(f"  postings read: {len(roles)}")
    print(f"  → open_jobs: present={sig['present']} strength={sig['strength']} "
          f"recency={sig['recency_days']} confidence={sig['confidence']}")
    if sig["roles"]:
        print("  above-store roles:")
        for r in sig["roles"]:
            age = f"{r['age_days']}d" if r["age_days"] is not None else "undated"
            print(f"    · {str(r['title'])[:52]:54} {str(r['location'] or '')[:24]:26} {age}")
    print(f"  unit-level: {sig['unit_level_count']}"
          + (f" (corroborates new_location)" if sig["unit_level_count"] else ""))
    if sig.get("probe_note"):
        print(f"  note: {sig['probe_note']}")
    if sig.get("hook_detail"):
        print(f"  hook: {sig['hook_detail']}")


if __name__ == "__main__":
    main()
