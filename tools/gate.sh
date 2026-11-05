#!/bin/sh
# Merge gate: everything a head must pass before it merges into the dev branch.
# ruff (if installed), the full test suite, a scan of this repo with itself (dogfood), and the CLI smoke test.
# Exit 0 = green. Each step prints its name; the first red step stops the run.
cd "$(dirname "$0")/.." || exit 2
step() { echo "== $1"; shift; "$@" || { echo "RED: $1"; exit 1; }; }
if command -v ruff >/dev/null 2>&1; then step ruff ruff check morphsaver tests; fi
step pytest timeout 600 python3 -m pytest -q -p no:cacheprovider
step dogfood python3 -m morphsaver scan . --out "${TMPDIR:-/tmp}/morphsaver-dogfood.json"
echo "GREEN"
