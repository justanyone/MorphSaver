Implement optional rank enrichment with standard-library adapters and policy weights.
Read the ticket and design before edits. Add fixtures before implementation.
Check missing tools, test references, deterministic reruns, and invalid tool output.
Run focused tests, then the required gate. Leave all commits to the launcher.
Fixture and adapter tests are next; rank already stores hot/tests/callers, so no JSON schema change is needed.
The 9 new tests failed before implementation. Added tool adapters, AST test references, rerun reset, and the hot weight; checking focused tests next.
Focused tests pass (9 tests, 1.67 s command wall time; rank fixture has 2 candidates). Added constant docs and checks for cached callers and stale evidence.
Moved the test-reference fixture under tests/references.py so pytest does not collect sample imports. The AST walker still sees it through the default exclude glob.
Focused rank and CLI checks passed (16 tests). Gate lint found two exception-type rules and a constant fixture assertion; fixed these before the whole-suite run.
