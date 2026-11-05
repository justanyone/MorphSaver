Fix the author post-check findings in the parallel-functions scanner.
Reduce collection and grouping complexity with small shared helpers.
Keep fixture behavior and stable candidate ids unchanged.
Run focused tests, then the offline gate. The launcher owns commits.
Collection fallback regression failed before the fix. Split collection and grouping; focused tests now run next.
Pyright: zero errors. Vulture and Refurb: no findings.
Commit measurements for the launcher: 300,000-line synthetic tree (300 modules, 30,000 functions): 10.836s; fixture candidates: [1, 0, 1].
300k-line full CLI scan met the 60s budget. Split import-base resolution too; run the final offline gate next.
Gate stopped before pytest: Ruff requires sorted fixture exports. Sorted them; rerun the gate.
Final: gate GREEN (18 tests, Ruff, dogfood); gate command completed in 0.714s. Focused suite: 10 passed.
All requested author findings fixed. No network or external-service tests needed. No git writes; launcher owns the commit and recorded measurements.
