# ADR 0001: Deterministic scan; a model judges only a bounded top-N

**Status:** Accepted 2026-11-04.
**Decision:** The CLI never calls a model. Scanners, ranking, packets and emitters are deterministic Python. A model reads at most `top` packets per run, each capped at `packet_max_lines`, and returns verdicts.
**Why:** On a 300k-line repository a model-driven scan costs tokens proportional to repository size and gives different answers each run. The prototype scan took under 10 s; judgment is the expensive part. Fixing N fixes the cost.
**Consequences:** Everything the judge needs must be in the packet. Candidate discovery quality is a scanner problem with fixtures, not a prompt problem. A host can run the scan on a timer with no model budget.
