# MORPH-M1-09 worker notes
- Plan: add emit/markdown depends_on for clump sharing a function with dispatch/parallel, skip unchanged writes, write tasks/README.md.
- Fixture first (tests/fixtures/emit/), then code, then test_cli three-candidate determinism.
- Done: emitter depends_on, skip-unchanged, tasks/README.md; tests added and focused tests pass. Next: gate, commit.
