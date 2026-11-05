# ADR 0002: State lives in `.morphsaver/` of the target; policy committed, runs ignored

**Status:** Accepted 2026-11-04 (owner interview).
**Decision:** MorphSaver reads `<target>/.morphsaver/policy.toml` and writes `<target>/.morphsaver/runs/<run>/`. The policy is meant to be committed; `runs/` is meant to be git-ignored.
**Why:** The tool is used standalone on a nearby directory as often as from a factory. A directory in the target keeps policy with the code it governs, and run outputs are per-run noise.
**Consequences:** The tool must create the directory. A target with no policy scans with defaults. Nothing is written outside the target.
