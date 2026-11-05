Implement M1-04 with fixtures before scanner changes.
Read architecture and ticket; preserve stable ids and signed costs.
Add per-file records and package-local grouping; test state and duplicate inputs.
Run focused offline tests, a 300k-line measurement, and the final gate.
Fixtures added first: four related functions, four unrelated shapes, and a package dict with an imported alias. CodeGraph index has no Python symbols; inspected named source directly.
Focused tests failed against the stub as expected. Implemented stateless function records, import/table resolution, skeleton grouping, and template-method costs. Next run focused tests.
Seven focused tests passed; one similarity fixture exceeded the intended edit size. Replaced it with one AST-node change and added CLI byte-stability coverage.
Nine focused tests pass, including concurrent runs, duplicate records, input validation, package isolation, and CLI output stability. Optimized subset removal before the 300k-line benchmark.
Full scan benchmark: 300000 generated lines, 100 modules, 10 packages, 10 candidates, 10.454 s.
Fixture counts: module positive 1 candidate / 4 sites; unrelated 0; package table 1 candidate / 3 sites. Use these measurements in the launcher commit message.
