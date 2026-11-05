# wx-morph-m1-05-data-clump notes
- Fix pass: vulture flagged unused names in tests/fixtures/clump/neg/c.py.
- Plan: call every name in the neg fixture from a __main__ block so no name is dead; the fixture stays a false positive.
- pyright: not installed here (FileNotFoundError), so it cannot run; reported as environment, not code.
- Next: run clump tests, then commit.
