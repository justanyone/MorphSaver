# Calibration

## 2026-11-04 prototype (dispatch_chain, exact-set repeated_dispatch)

| Tree | Lines | Chains, 4+ arms | Chains, 3+ arms | Same value set at 2+ sites | Runtime |
|---|---|---|---|---|---|
| repo A `src/` (build factory) | 300,824 | 10 | 31 | 2 | 7.9 s |
| repo B `src/` (document service) | 450,883 | 6 | 19 | 1 | 6.6 s |

Largest single chains: 22 arms on an event name (61 arm lines, state-machine handler), 8 arms on an HTML tag name, 7 arms on a
command kind, 6 arms on a field name, 4 arms with 64 lines in a parameter validator. Both repositories already use module-level
dict dispatch tables (187 in repo A).

Reading: the textbook repeated-switch smell is rare in code that already uses tables. The value will come from
`parallel_functions` and `data_clump` (not yet measured) and from judging the few large single-site handlers.

Precision per scanner: not measured yet (ticket M1-10).
