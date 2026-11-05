# MorphSaver

MorphSaver finds places in a large codebase where a set of `if/elif` or `match` arms, a family of look-alike functions,
or a recurring clump of parameters would be simpler as a class hierarchy, a dispatch table or a dataclass. It then writes
each worthwhile change up as a task that a coding session (Claude Code, Codex, or any agent that can read markdown) can execute.

It is built for repositories over 100k lines. The scan is deterministic Python with no model call and runs in seconds.
A model only ever reads a bounded set of evidence packets and gives verdicts. Nothing in the tool talks to a model API.

## Install

```sh
pipx install .                    # from a checkout of this repository
# or: python3 -m venv .venv && .venv/bin/pip install .
morphsaver --version              # prints 0.1.0
```

Python 3.11 or newer, no dependencies. Optional: `ruff`, `radon` and `codegraph` on PATH enrich the ranking.

## Use

```sh
cd your-repo
mkdir -p .morphsaver && cp /path/to/MorphSaver/docs/policy.example.toml .morphsaver/policy.toml  # optional
morphsaver run .                 # scan + rank + packet -> .morphsaver/runs/<timestamp>/
ls .morphsaver/runs/*/packets    # one markdown packet per candidate, ready for a judge
```

Then a session judges the packets (see `skills/morphsaver-judge/SKILL.md`) and writes `verdicts.json`, and

```sh
morphsaver emit . --format markdown    # one task file per accepted candidate
```

Commit `.morphsaver/policy.toml`; git-ignore `.morphsaver/runs/`.

## Pipeline

| Step | Who | Reads | Writes |
|---|---|---|---|
| `scan` | CLI, deterministic | source files, `policy.toml` | `candidates.json` |
| `rank` | CLI, deterministic | `candidates.json` | `ranked.json` |
| `packet` | CLI, deterministic | `ranked.json`, source | `packets/*.md` |
| judge | a session (skill) | `packets/*.md` | `verdicts.json` |
| `emit` | CLI, deterministic | `verdicts.json` | `tasks/*` in a chosen format |
| execute | a session (skill) | one task | a branch with green tests |

Design: [docs/design/architecture.md](docs/design/architecture.md). Decisions: [docs/adr](docs/adr). Work plan: [docs/tasks.md](docs/tasks.md).

## Status

Pre-alpha. The `dispatch_chain` scanner, exact-value `repeated_dispatch`, the cost model, packets and the markdown emitter work
on fixtures and on MorphSaver itself. The other scanners, tool enrichment, the GitHub and build-factory emitters and the
judge skill are open tickets in `docs/tasks.md`.

## License

MIT. Copyright (c) 2026 Kevin J. Rice.

## Development cycles

- dev-001 started 2026-11-04: milestone 1 (scan, rank, packet, markdown emit for Python).
