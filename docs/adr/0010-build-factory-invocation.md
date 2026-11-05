# ADR 0010: How a build factory invokes MorphSaver

**Status:** Accepted 2026-11-04 (owner interview).
**Decision:** A build factory runs MorphSaver as a scan step with no model call, on a timer, from a pinned MorphSaver version, inside its own cycle. The step posts one judge task per batch of packets; the judge task's worker writes `verdicts.json` and runs `emit` with the factory emitter; each accepted verdict becomes one fix task. Re-running files no duplicates: task keys derive from candidate ids.
**Why:** Mirrors how the owner's factory already runs a no-model complexity scan that files refactor tasks, and keeps the model budget inside tasks the factory already meters. Two-tier models (cheap first) are the owner's standing preference.
**Consequences:** The factory keeps a `.morphsaver/policy.toml` in its own repository and a glue script in its kit. MorphSaver itself has no knowledge of the factory beyond the emitter plugin's environment variables.
