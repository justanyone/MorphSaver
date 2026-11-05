# ADR 0011: Nothing is denied by default; deny and caution are opt-in per target

**Status:** Accepted 2026-11-04 (owner interview: the largest hit in the owner's factory, a 22-arm state-machine event handler, gets no special treatment).
**Decision:** With no policy, every included file is scanned and every candidate is judged like any other. `deny` globs suppress reporting; `caution` globs force verdict `ask-owner`. Both are empty by default.
**Why:** The owner wants to see the big handlers even when the answer is "leave it". Hiding by default would make the tool look blind on exactly the code that matters.
**Consequences:** A target that has protected code writes it in its own policy. The judge rubric treats `policy: caution` as a hard `ask-owner`.
