"""Put the repo's script directories on sys.path. Every test module imports this first.

The scripts are invoked by path in the runbooks, not installed, so tests reach them the same way the
runbooks do rather than pretending there is a package.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for rel in ("lib", "scripts", os.path.join("hubspot-app", "scripts")):
    path = os.path.join(ROOT, rel)
    if path not in sys.path:
        sys.path.insert(0, path)
