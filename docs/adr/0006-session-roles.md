# ADR 0006: Three session roles: scan, judge, execute

**Status:** Accepted 2026-11-04 (owner interview: judge runs as a factory task per batch, cheap model first).
**Decision:** A MorphSaver session is one of three roles, never two at once.
- scan: runs the CLI, reports the top of `ranked.json`, judges nothing.
- judge: reads packets in rank order, writes `verdicts.json`, runs `emit`. Cheap model first; a stronger model may re-read `accept`s above a threshold.
- execute: takes one emitted task, keeps behaviour, keeps the listed tests green, one site per commit when more than 3 sites, reports the signed line delta, and may return `reject` with a reason instead of forcing a refactor.
**Why:** Separating roles bounds each session's context and cost, makes each output checkable, and lets a factory schedule them as distinct tasks.
**Consequences:** Each role has a `SKILL.md` and an `AGENTS.md` section. A task that needs a new role stops and asks the owner.
