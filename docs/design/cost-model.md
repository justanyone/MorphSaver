# Cost model

Implemented in `morphsaver/rank.py`. All constants come from `[weights]` and `[thresholds]` in `policy.toml`.

| Term | Meaning | Default |
|---|---|---|
| `dup_lines` | arm-body lines summed over every site in the candidate | measured |
| `class_overhead` | lines one subclass costs (class line, method line, two of body/blank) | 4 |
| `base_overhead` | lines the base class and its abstract method cost | 6 |
| registry | one line per arm for the table or registry | n_arms |
| `lines_saved` | `dup_lines - (n_arms * class_overhead + base_overhead + n_arms)`; signed | computed |
| `sites_weight` | multiplier on a positive `lines_saved` when more than one site collapses | 1.5 |
| `site_bonus` | added per extra site, whatever the sign, so repetition outranks a lone chain of the same size | 2.0 |
| `risk_weight` | subtracted per caller of the enclosing functions (needs CodeGraph; unknown = 0) | 0.2 |
| `no_tests_penalty` | subtracted when no test references the enclosing functions | 10 |

Shape rule: single site and `lines_saved <= 0` gives `dict-table`; otherwise `dispatch_chain` and `repeated_dispatch`
give `strategy-classes`, `parallel_functions` gives `template-method`, `data_clump` gives `dataclass-param`,
`flag_argument` gives `split-function`. The judge may change the shape.

Order: by score descending, then site count descending, then id. Deterministic by test.

Open calibration questions (ticket M1-07): are 4 and 6 right for Python with type hints and docstrings; should `match`
arms count less overhead than if/elif since a `match` already is a table.

For `template-method`, `dup_lines` is the sum of function body lines.
Overhead is `base_overhead + member_count * class_overhead`.
Count one base and one override per member. No dispatch registry is needed.
Report negative savings without a lower bound.
