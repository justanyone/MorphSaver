# Using MorphSaver from a build factory

This page is generic. A factory keeps its own glue and policy in its own repository (ADR 0008, ADR 0010).

1. **Project record.** Register MorphSaver as a project of the factory with `tools/test.sh` as the test command and
   `tools/gate.sh` as the gate, pull-request merge mode, base branch `dev-001`, at lower priority than the factory's main projects.
2. **Policy in the scanned repository.** Commit `.morphsaver/policy.toml` in the repository the factory will scan. Git-ignore `.morphsaver/runs/`.
3. **Scan step.** A cycle step runs, with no model call, from a pinned MorphSaver version:
   `morphsaver run <repo> --top 25`, then `morphsaver diff <previous-run> <this-run>` to find new candidate ids.
4. **Judge task.** The step files one task per batch of new packets. Its worker follows `skills/morphsaver-judge/SKILL.md`,
   runs `morphsaver check`, then `morphsaver emit --format <factory-plugin> --execute`.
5. **Fix tasks.** The emitter posts one task per accepted verdict, key derived from the candidate id, so re-runs file no
   duplicates. The factory's existing refactor cap bounds open MorphSaver tasks.
6. **Execute.** The factory's workers follow `skills/morphsaver-execute/SKILL.md` for each fix task.

Environment for the factory emitter: `MORPHSAVER_TASK_API` (base URL), `MORPHSAVER_TASK_TOKEN_FILE` (bearer token path),
`MORPHSAVER_TASK_PROJECT` (project id). Nothing else is read from the environment.
