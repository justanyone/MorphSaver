# Calibration

## 2026-11-04 prototype (dispatch_chain, exact-set repeated_dispatch)

| Tree | Lines | Chains, 4+ arms | Chains, 3+ arms | Same value set at 2+ sites | Runtime |
|---|---|---|---|---|---|
| repo A `src/` | 300,824 | 10 | 31 | 2 | 7.9 s |
| repo B `src/` | 450,883 | 6 | 19 | 1 | 6.6 s |

Largest single chains: 22 arms on an event name (61 arm lines, state-machine handler), 8 arms on an HTML tag name, 7 arms on a
command kind, 6 arms on a field name, 4 arms with 64 lines in a parameter validator. Both repositories already use module-level
dict dispatch tables (187 in repo A).

Reading: the textbook repeated-switch smell is rare in code that already uses tables. The value will come from
`parallel_functions` and `data_clump` (not yet measured) and from judging the few large single-site handlers.

Precision per scanner: not measured yet (ticket M1-10).

## 2026-11-05 calibration

Two distinct local repositories were available. Python source was copied into
ignored run directories in this worktree. No source checkout was changed.
The inputs contain `src/`, `tests/`, and `scripts/`. Counts use physical Python
lines, including blank lines and comments. The default policy excludes tests.
No target policy file was copied. These are new inputs, not the prototype inputs.

| Input | Python files | Python lines | Source copy/count | Test/script copy/count |
|---|---:|---:|---:|---:|
| repo A | 3,395 | 994,231 | 0.273 s | 7.123 s |
| repo B | 1,209 | 822,724 | 1.795 s | 1.403 s |

Each input uses `python3 -m morphsaver run <input> --top 25 --run calibration`.
Scan, rank, and packet times use a monotonic clock at each CLI output line.
Scan time includes interpreter startup. These are elapsed times, not CPU times.

The runs are in progress. Precision is not measured yet. No default has changed.
There is no evidence yet to support a threshold change.

### Offline checks

The focused rank and CLI checks passed: 35 tests.
The fixture baseline used 26 Python files and took 0.051 s.
Candidate counts were: `dispatch_chain` 20, `repeated_dispatch` 4,
`parallel_functions` 2, `data_clump` 2, and `flag_argument` 2.
This is a combined fixture scan with path exclusions disabled. It is not a
precision sample. No scanner, schema, state, or launch behavior was changed.

### Later fixture tickets

No new missed or false candidate has been established yet.
