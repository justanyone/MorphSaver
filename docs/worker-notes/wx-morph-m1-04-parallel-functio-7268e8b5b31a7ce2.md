Implement M1-04 with fixtures before scanner changes.
Read architecture and ticket; preserve stable ids and signed costs.
Add per-file records and package-local grouping; test state and duplicate inputs.
Run focused offline tests, a 300k-line measurement, and the final gate.
Fixtures added first: four related functions, four unrelated shapes, and a package dict with an imported alias. CodeGraph index has no Python symbols; inspected named source directly.
Focused tests failed against the stub as expected. Implemented stateless function records, import/table resolution, skeleton grouping, and template-method costs. Next run focused tests.
Seven focused tests passed; one similarity fixture exceeded the intended edit size. Replaced it with one AST-node change and added CLI byte-stability coverage.
