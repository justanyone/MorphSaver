Implement M1-03 with deterministic Jaccard connected groups across files.
Add repeated-dispatch fixtures before scanner edits, including weak overlap and enum names.
Check stable union ids, policy levels, and repeat-run output with focused tests.
Run the offline gate and record runtime and fixture counts for the launcher.
Fixtures now cover three-file overlap, weak overlap, and enum/bare/literal equivalence; regression tests cover state, concurrency, thresholds, and duplicate inputs.
The initial focused run failed on missing overlap sites, input order/duplicates, and invalid thresholds. After the fix, all 18 focused tests pass. Added the exact 0.6 boundary and transitive union regression next.
