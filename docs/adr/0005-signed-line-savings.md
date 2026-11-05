# ADR 0005: Signed line savings; negative is reported, never hidden

**Status:** Accepted 2026-11-04.
**Decision:** `lines_saved = dup_lines - overhead` is reported as computed, including negative values. A single-site candidate with `lines_saved <= 0` is shaped `dict-table` rather than dropped.
**Why:** Calibration showed most hits in real repositories are single-site chains where a class hierarchy adds lines. A tool that clamps at zero "finds" refactors that grow the code. The owner wants to see large single-site handlers even when the answer is "leave it".
**Consequences:** The judge may revise the estimate. Emitted tasks state the signed estimate and the execute session reports the measured delta.
