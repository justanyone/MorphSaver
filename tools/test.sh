#!/bin/sh
# Worker test command: `tools/test.sh [pytest args]...` (a factory's test step calls this).
# Pure stdlib project: no install step. Limit 600 s. Prints the last 60 lines; exit code is pytest's.
cd "$(dirname "$0")/.." || exit 2
out=$(mktemp "${TMPDIR:-/tmp}/morphsaver-test.XXXXXX") || exit 2
timeout 600 nice -n 10 python3 -m pytest -q -p no:cacheprovider "$@" >"$out" 2>&1
rc=$?
tail -60 "$out"
rm -f "$out"
exit $rc
