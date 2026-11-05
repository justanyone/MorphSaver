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
| `hot_bonus` | added per distinct ruff code or radon rank | 3.0 |
| `risk_weight` | subtracted per caller of the enclosing functions (needs CodeGraph; unknown = 0) | 0.2 |
| `no_tests_penalty` | subtracted when no test references the enclosing functions | 10 |

Shape rule: single site and `lines_saved <= 0` gives `dict-table`; otherwise `dispatch_chain` and `repeated_dispatch`
give `strategy-classes`, `parallel_functions` gives `template-method`, `data_clump` gives `dataclass-param`,
`flag_argument` gives `split-function`. The judge may change the shape.

Order: by score descending, then site count descending, then id. Deterministic by test.

Open calibration questions: are 4 and 6 right for Python with type hints and docstrings; should `match`
arms count less overhead than if/elif since a `match` already is a table.

For `template-method`, `dup_lines` is the sum of function body lines.
Overhead is `base_overhead + member_count * class_overhead`.
Count one base and one override per member. No dispatch registry is needed.
Report negative savings without a lower bound.

`hot_bonus` adds 3.0 per distinct hot code. Ruff codes are `C901`, `PLR0912`, and `PLR0911`.
Radon ranks use `radon:<letter>`. The score adds `len(set(hot)) * hot_bonus`.
Set `hot_bonus` in `[weights]` to change this value.

Rank reads test references from Python files that match the policy exclude globs.
An AST name, attribute, or import must name an enclosing function.
Comments and string literals do not count. A reference removes `no_tests_penalty`.
CodeGraph supplies caller counts. Unknown counts do not add risk.
Missing tools each cause one warning. Rank still succeeds.
Each rank run replaces the previous evidence. Hot codes and test paths are sorted.

The other numeric policy constants are in `[thresholds]`:

| Constant | Meaning | Default |
|---|---|---|
| `min_arms` | Minimum dispatch arms | 3 |
| `min_sites` | Minimum repeated dispatch sites | 2 |
| `jaccard` | Minimum value-set overlap | 0.6 |
| `skeleton_similarity` | Minimum function shape similarity | 0.8 |
| `top` | Default packet count | 25 |
| `packet_max_lines` | Maximum lines per packet | 400 |

Radon JSON can report numeric complexity without a rank letter.
Rank converts scores 0–5 to A, 6–10 to B, 11–20 to C,
21–30 to D, 31–40 to E, and 41 or more to F.
These ranges define Radon ranks. They are not score weights.
Invalid complexity values add no hot code.
