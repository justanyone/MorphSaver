# wx-morph-m1-09-emit-deps notes
- Task: fix author post-check findings (vulture unused NAME/fixture functions, refurb FURB115/FURB124 in tests/test_emit_deps.py).
- Fix: __all__ in markdown.py and fixture; refurb rewrites in test. No behaviour change.
- Next: run tools/test.sh tests/test_emit_deps.py tests/test_cli.py, then tools/gate.sh.
- Last: gate GREEN; vulture and refurb not run here (not in gate.sh); changes left uncommitted for the launcher.
