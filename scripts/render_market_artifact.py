#!/usr/bin/env python3
"""Render the UKI Market Signals artifact from the conjunctural register + market context.

The artifact (knowledge/conjunctural/README.md — "the rep-facing surface of the register") is a single
self-contained HTML page: an interactive matcher that mirrors scripts/conjunctural_match.py client-side,
a dated-events timeline, and the sector-context cards from knowledge/conjunctural/market_context.json.
This script exists so the monthly register refresh regenerates the page reproducibly instead of the
artifact drifting from the data (the US repo's recap was a one-off snapshot; this one is rebuildable).

USAGE
    python3 scripts/render_market_artifact.py            # → output/reports/uki_market_signals.html
    python3 scripts/render_market_artifact.py --out /path/page.html

FONTS — brand faces are licensed files and NOT committed. The script embeds them from local paths
(override with env NORY_FONT_SHARP / NORY_FONT_GRAPHIK); if missing it falls back to the system stack
and says so, rather than failing: a readable page without brand faces beats no page.

Requires only stdlib. The page must stay ≤16 MB published; this build is ~200 KB.
"""
import argparse
import base64
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

FONT_SHARP = os.environ.get("NORY_FONT_SHARP", os.path.expanduser("~/Downloads/SharpGrotesk-Bold20.otf"))
FONT_GRAPHIK = os.environ.get("NORY_FONT_GRAPHIK", os.path.expanduser("~/Downloads/Graphik-Medium-Web.woff2"))


def b64_or_empty(path, name):
    if not os.path.isfile(path):
        print(f"WARNING: {name} not found at {path} — shipping with the fallback font stack", file=sys.stderr)
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def load_register():
    entries = []
    for path in sorted(glob.glob(os.path.join(REGISTER_DIR, "*.json"))):
        with open(path) as f:
            data = json.load(f)
        entries.extend(data.get("entries", []))
    if not entries:
        sys.exit("FATAL: no register entries — the artifact would be an empty shell.")
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

    sharp = b64_or_empty(FONT_SHARP, "Sharp Grotesk")
    graphik = b64_or_empty(FONT_GRAPHIK, "Graphik")
    if sharp:
        html = html.replace("__SHARP__", sharp)
    else:
        html = html.replace(
            "@font-face{font-family:'Sharp Grotesk';src:url(data:font/otf;base64,__SHARP__) format('opentype');font-weight:700;font-display:swap}", "")
    if graphik:
        html = html.replace("__GRAPHIK__", graphik)
    else:
        html = html.replace(
            "@font-face{font-family:'Graphik';src:url(data:font/woff2;base64,__GRAPHIK__) format('woff2');font-weight:400 600;font-display:swap}", "")

    html = html.replace("__REGISTER__", json.dumps(entries, ensure_ascii=False))
    html = html.replace("__CTX__", json.dumps(ctx, ensure_ascii=False))

    for marker in ("__REGISTER__", "__CTX__", "__SHARP__", "__GRAPHIK__"):
        if marker in html:
            sys.exit(f"FATAL: unreplaced placeholder {marker} — template and script are out of sync.")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(html)
    print(f"rendered {args.out}  ({os.path.getsize(args.out)//1024} KB, {len(entries)} register entries, {len(ctx)} context cards)")


if __name__ == "__main__":
    main()
