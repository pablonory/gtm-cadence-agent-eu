#!/usr/bin/env python3
"""Shared helpers. Stdlib only, Python 3.9-compatible — every script here promises that.

Not a package: scripts are invoked by path (the runbooks document them that way), so callers add this
directory to sys.path off their own __file__ rather than relying on a cwd or an install step:

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
    from gtm_common import load_dotenv, normalize_domain

Started 2026-08-24 to kill duplication that had already caused real bugs:
  - `_load_dotenv` existed in 5 copies, and 2 of them did not strip quotes, so a quoted token in .env
    authenticated in three scripts and 401'd in two.
  - domain normalisation existed in 4 divergent forms (one of them a no-op), which is why a HubSpot
    company stored as `www.machapresso.com` broke the pipeline.

A HubSpot client with retry/backoff/rate-limiting belongs here too and is not written yet.
"""
import os


def load_dotenv(start=None):
    """Load KEY=VALUE lines from the nearest .env walking up from `start` (default: this file).

    Real environment wins — this only fills gaps, so `FOO=x python3 script.py` still overrides.
    Strips surrounding quotes and a leading `export `, both of which appear in hand-written .env files.
    """
    here = os.path.dirname(os.path.abspath(start or __file__))
    for _ in range(6):
        candidate = os.path.join(here, ".env")
        if os.path.isfile(candidate):
            with open(candidate) as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("export "):
                        line = line[len("export "):].strip()
                    if "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                        value = value[1:-1]
                    if key:
                        os.environ.setdefault(key, value)
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return None


def normalize_domain(raw):
    """Canonical form of an account domain. The upsert key — one implementation, everywhere.

    lowercase, drop scheme, drop any path/query/fragment, drop userinfo and port, trim dots/spaces,
    then strip EXACTLY ONE leading `www.`.

    Deliberately conservative about subdomains: only `www.` is removed. `jobs.lever.co` must survive
    intact because jobs_probe.py resolves ATS boards by hostname, and `www.www.x.com` (a real typo
    shape) collapses one level only, so the oddity stays visible instead of being silently cleaned.

    Returns "" for None/empty rather than raising — callers decide whether a missing domain is fatal.
    """
    if not raw:
        return ""
    d = str(raw).strip().lower()
    if "//" in d:
        d = d.split("//", 1)[1]
    for sep in ("/", "?", "#"):
        if sep in d:
            d = d.split(sep, 1)[0]
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    if ":" in d:
        d = d.split(":", 1)[0]
    d = d.strip().strip(".")
    if d.startswith("www."):
        d = d[4:]
    return d
