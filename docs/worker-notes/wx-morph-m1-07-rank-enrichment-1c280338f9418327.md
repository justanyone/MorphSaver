Implement optional rank enrichment with standard-library adapters and policy weights.
Read the ticket and design before edits. Add fixtures before implementation.
Check missing tools, test references, deterministic reruns, and invalid tool output.
Run focused tests, then the required gate. Leave all commits to the launcher.
Fixture and adapter tests are next; rank already stores hot/tests/callers, so no JSON schema change is needed.
The 9 new tests failed before implementation. Added tool adapters, AST test references, rerun reset, and the hot weight; checking focused tests next.
Focused tests pass (9 tests, 1.67 s command wall time; rank fixture has 2 candidates). Added constant docs and checks for cached callers and stale evidence.
Moved the test-reference fixture under tests/references.py so pytest does not collect sample imports. The AST walker still sees it through the default exclude glob.
Focused rank and CLI checks passed (16 tests). Gate lint found two exception-type rules and a constant fixture assertion; fixed these before the whole-suite run.
Gate lint is green. Full offline pytest and the repository self-scan are running; no dependency or schema changes were needed.
Completed: tools/gate.sh printed GREEN; lint passed, all 54 tests passed, and the self-scan found 3 candidates in 18 files.
Measured fixture result: 2 dispatch candidates; only handle has tests/references.py. Initial passing focused run: 9 tests, 1.67 s command wall time; expanded focused run: 16 tests passed.
All checks ran offline. No tests remain blocked. No git writes or commits were performed by this session; the launcher owns commits and can use these measurements.
Final: optional enrichment, hot_bonus policy loading, constant docs, fixtures, and regression tests are complete. No remaining work.
