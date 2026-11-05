Implement optional rank enrichment with standard-library adapters and policy weights.
Read the ticket and design before edits. Add fixtures before implementation.
Check missing tools, test references, deterministic reruns, and invalid tool output.
Run focused tests, then the required gate. Leave all commits to the launcher.
Fixture and adapter tests are next; rank already stores hot/tests/callers, so no JSON schema change is needed.
The 9 new tests failed before implementation. Added tool adapters, AST test references, rerun reset, and the hot weight; checking focused tests next.
