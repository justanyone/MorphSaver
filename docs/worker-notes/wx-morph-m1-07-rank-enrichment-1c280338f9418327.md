I will fix the rank enrichment review findings within this worktree.
I will preserve policy fields and fixture controls that are part of the public contract.
I will add regression coverage before reducing enrichment complexity.
I will run focused offline tests and the final gate, then record measured results.
The launcher owns all commits and pushes.
Focused rank tests pass: 13 tests. Extracted hot-code and caller helpers; kept caller caches local to each run.
Policy findings are false positives: scanner and packet code read every flagged field and method. The unreferenced fixture function is an intentional test-reference control.
Added coverage for failed caller queries: one warning per tool and one query per distinct function, including duplicate candidates.
