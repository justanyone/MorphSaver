# Architecture decision records

One file per decision. Status: Proposed, Accepted, Superseded. An ADR is never edited after acceptance except to add a
superseded note; write a new one. Decisions 0001 to 0011 were accepted by the owner on 2026-11-04 in an interview.

| ADR | Title |
|---|---|
| [0001](0001-deterministic-scan-model-judges-top-n.md) | Deterministic scan; a model judges only a bounded top-N |
| [0002](0002-state-in-dot-morphsaver.md) | State lives in `.morphsaver/` of the target; policy committed, runs ignored |
| [0003](0003-one-file-per-step.md) | One JSON file per pipeline step; every step resumable; schema versioned |
| [0004](0004-judge-may-not-add-candidates.md) | The judge may not add candidates; verdict vocabulary is fixed |
| [0005](0005-signed-line-savings.md) | Signed line savings; negative is reported, never hidden |
| [0006](0006-session-roles.md) | Three session roles: scan, judge, execute |
| [0007](0007-host-agnostic-sessions.md) | Host-agnostic: a SKILL.md per role for Claude Code, AGENTS.md for Codex; the host needs only the CLI and markdown |
| [0008](0008-emitters-are-plugins.md) | Emitters are plugins; no host-project text in the core |
| [0009](0009-python-first-tree-interface.md) | Python `ast` in v1 behind a parse-tree scanner interface |
| [0010](0010-build-factory-invocation.md) | How a build factory invokes MorphSaver: no-model scan step, one judge task per batch, fix tasks per accepted verdict |
| [0011](0011-nothing-denied-by-default.md) | Nothing is denied by default; deny and caution are opt-in per target |
