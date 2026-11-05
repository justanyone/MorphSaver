Fix the author post-check findings in the parallel-functions scanner.
Reduce collection and grouping complexity with small shared helpers.
Keep fixture behavior and stable candidate ids unchanged.
Run focused tests, then the offline gate. The launcher owns commits.
Collection fallback regression failed before the fix. Split collection and grouping; focused tests now run next.
Pyright: zero errors. Vulture and Refurb: no findings.
Commit measurements for the launcher: 300,000-line synthetic tree (300 modules, 30,000 functions): 10.836s; fixture candidates: [1, 0, 1].
