# ADR 0004: The judge may not add candidates; verdict vocabulary is fixed

**Status:** Accepted 2026-11-04.
**Decision:** The judge session fills `verdict`, `rationale` and optionally `revised_lines_saved` on the candidates it was given. It may not add, merge or split candidates. Verdicts are exactly `accept`, `dict-table`, `reject`, `ask-owner`.
**Why:** Keeps the output reproducible and keeps the model from wandering the repository. A missed candidate is a scanner bug with a fixture, which improves every future run.
**Consequences:** When a judge sees something the scanner missed, it writes the observation in the rationale of the nearest candidate or in a notes file; the fix is a scanner ticket.
