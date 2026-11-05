# MorphSaver: rules for coding agents

Read this before changing anything. Claude Code sessions: `CLAUDE.md` points here. Codex sessions: this file is yours.

## What this repo is
A deterministic scanner plus session instructions. The CLI (`morphsaver`) never calls a model. Sessions judge and execute.
Design in `docs/design/architecture.md`; decisions in `docs/adr/`; tickets in `docs/tasks.md`.

## Rules
- Python 3.11+, stdlib only in `morphsaver/`. Optional tools (ruff, radon, codegraph) are detected with `shutil.which` and never required.
- Every scanner has a fixture with one true positive and one known false positive under `tests/fixtures/<scanner>/`.
- `scan`, `rank`, `emit` are deterministic: same input, byte-identical output. A test asserts it.
- Candidate ids are stable across runs (hash of file, function, discriminator). Never derive an id from a line number.
- Signed line savings are always reported. Never clamp `lines_saved` at zero.
- No host-project text in the core. The build-factory emitter reads its service from `MORPHSAVER_TASK_*` environment variables.
- Schema changes bump `SCHEMA_VERSION` and get a migration note in `docs/design/architecture.md`.
- Tests under 1 minute total. `tools/test.sh` runs them; `tools/gate.sh` is the merge gate.
- Keep MorphSaver's own policy in `.morphsaver/policy.toml`; the gate scans this repo with itself.

## Working a ticket from docs/tasks.md
1. Read the ticket's acceptance criteria. They are the definition of done.
2. Add or update the fixture first, then the code.
3. Run `tools/gate.sh`. Green is required before a pull request.
4. Put the measured numbers (runtime, candidate counts on fixtures) in the commit message.

## Session roles (ADR 0006)
- scan session: runs the CLI, nothing else.
- judge session: reads packets, writes `verdicts.json`; may not add candidates.
- execute session: takes one emitted task, keeps behaviour, keeps listed tests green, one site per commit when more than 3 sites.
