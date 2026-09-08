#!/usr/bin/env python3
"""Render the UKI Market Signals page from the conjunctural register + market context.

The page (knowledge/conjunctural/README.md — "the rep-facing surface of the register") is one
self-contained HTML file: an interactive matcher that mirrors scripts/conjunctural_match.py
client-side, a dated-events calendar, and the sector-context rows from
knowledge/conjunctural/market_context.json. This script exists so the fortnightly refresh
regenerates the page reproducibly instead of the artefact drifting from the data.

Redesigned 2026-09-08 for function over form: system font stack, no embedded brand fonts, one
accent, semantic colour only where it carries meaning. ~60 KB output.

USAGE
    python3 scripts/render_market_artifact.py            # → output/reports/uki_market_signals.html
    python3 scripts/render_market_artifact.py --out /path/page.html

Requires only stdlib.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
TEMPLATE = os.path.join(ROOT, "knowledge", "conjunctural", "artifact_template.html")
REGISTER_DIR = os.path.join(ROOT, "knowledge", "conjunctural", "register")
CONTEXT = os.path.join(ROOT, "knowledge", "conjunctural", "market_context.json")
DEFAULT_OUT = os.path.join(ROOT, "output", "reports", "uki_market_signals.html")


def load_register():
    entries = []
    for path in sorted(glob.glob(os.path.join(REGISTER_DIR, "*.json"))):
        with open(path) as f:
            entries.extend(json.load(f).get("entries", []))
    if not entries:
        sys.exit("FATAL: no register entries — the page would be an empty shell.")
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    with open(TEMPLATE) as f:
        html = f.read()
    entries = load_register()
    with open(CONTEXT) as f:
        ctx = json.load(f)["cards"]

    html = html.replace("__REGISTER__", json.dumps(entries, ensure_ascii=False))
    html = html.replace("__CTX__", json.dumps(ctx, ensure_ascii=False))
    for marker in ("__REGISTER__", "__CTX__", "__EVENTS__"):
        if marker in html:
            sys.exit(f"FATAL: unreplaced placeholder {marker} — template and script are out of sync.")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(html)
    print(f"rendered {args.out}  ({os.path.getsize(args.out)//1024} KB, {len(entries)} register entries, {len(ctx)} context rows)")


if __name__ == "__main__":
    main()
