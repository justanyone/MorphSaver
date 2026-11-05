Implement M1-03 with deterministic Jaccard connected groups across files.
Add repeated-dispatch fixtures before scanner edits, including weak overlap and enum names.
Check stable union ids, policy levels, and repeat-run output with focused tests.
Run the offline gate and record runtime and fixture counts for the launcher.
Fixtures now cover three-file overlap, weak overlap, and enum/bare/literal equivalence; regression tests cover state, concurrency, thresholds, and duplicate inputs.
The initial focused run failed on missing overlap sites, input order/duplicates, and invalid thresholds. After the fix, all 18 focused tests pass. Added the exact 0.6 boundary and transitive union regression next.
All 19 focused tests pass; CLI integration now expects 16 candidates (12 single chains and 4 groups). The first gate stopped at lint because enum fixtures lacked symbol definitions; added real Enum definitions and bare aliases before rerunning.
Validation complete: tools/gate.sh printed GREEN; ruff passed, 41 tests passed, and self-scan found 2 candidates in 17 files. Gate runtime was 1.819 seconds.
Launcher commit measurements: repeated fixtures scanned in 0.006958 seconds; overlap 3 chains / 1 group / 3 sites, weak 2 chains / 0 groups, enum 3 chains / 1 group / 3 sites. Focused suite: 19 passing tests.
Finished: deterministic Jaccard components, sorted union ids, highest member policy, threshold validation, and duplicate-input handling are on disk. No schema change, dependencies, network access, or remaining work. The launcher handles commits and pushes.
