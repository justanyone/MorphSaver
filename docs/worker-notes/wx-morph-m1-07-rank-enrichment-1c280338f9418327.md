Review the current rank enrichment and the author post-check findings.
Preserve policy fields used by scanners and verify their runtime use.
Add regression coverage before changing code, then run focused tests and the gate.
Keep changes inside this worktree. The launcher handles commits and pushes.
Policy findings are false positives: scanners read all named thresholds and path_policy; packet reads packet_max_lines. Radon JSON coverage uses a synthetic rank field; add a real numeric-complexity fixture and regression next. The first codegraph output exceeded the requested bound; all later reads are bounded.
Numeric Radon fixture failed before the fix, then all 14 rank tests passed. Added numeric rank conversion without dependencies. Existing tests cover concurrent independent runs, replaced state, invalid output, and cached duplicate caller queries. Next verify rank boundaries and run the gate.
Final verification: 31 focused rank tests passed in 0.61 s; tools/gate.sh printed GREEN in 4.84 s with 73 tests, ruff, and self-scan (18 files, 3 candidates). Rank fixture has 2 candidates: 1 test-referenced and 1 known reference false positive. Numeric Radon fixture supplies 2 hot ranks.
Post-check disposition: package-wide Vulture no longer reports the six policy symbols; they have real callers. Fixture functions are AST input and intentionally need no Python caller. Retain them to preserve scanner coverage. Pyright is not installed, so its unavailable-report finding could not be reproduced; no network or dependencies were added.
Finished: numeric Radon conversion, regression tests, and documentation are complete. No git writes or external changes. Launcher commit measurements: focused 0.61 s, gate 4.84 s, fixture 2 candidates, self-scan 3 candidates.
