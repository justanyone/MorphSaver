Review the existing Jaccard implementation and its fixture coverage.
Fix the reported post-check issue within the ticket paths, with fixtures first.
Run focused offline tests, then the required gate once.
Record runtimes and fixture counts here for the launcher commit message.
Existing coverage includes state, concurrent calls, invalid thresholds, duplicate input, and stable ids. Added a qualified enum fixture before code changes. Pyright is not installed; no dependency will be added.
The qualified enum regression failed with 3 sites instead of 4 before the fix. Corrected an overly broad test edit. Normalization now accepts qualified enum names and preserves dotted literals and numbers. Extracted group construction and removed a nested pair loop to reduce complexity; 19 focused tests passed.
Validation complete: focused suite 20 passed; tools/gate.sh printed GREEN with ruff, 42 tests, and self-scan in 1.49 s. Fixture scans took 0.0087 s: overlap 3 chains -> 1 group/3 sites; weak 2 chains -> 0 groups; enum 4 chains -> 1 group/4 sites.
Final: all ticket behavior is implemented and verified offline. Pyright could not run because its executable is absent. No dependencies or schema changes. No git writes or network calls; launcher owns the commit and should include the measurements above.
