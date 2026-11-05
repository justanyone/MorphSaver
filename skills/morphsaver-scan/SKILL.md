---
name: morphsaver-scan
description: Run MorphSaver on a repository to find conditional-to-polymorphism and parallel-structure refactor candidates. Use when asked to scan a codebase for switch/if-elif chains that should be classes, dispatch tables, or dataclasses, or to produce refactor packets.
---

# MorphSaver scan

1. `python3 -m morphsaver run <repo> --top 25` (or `morphsaver run` when installed). Needs Python 3.11+.
2. Outputs land in `<repo>/.morphsaver/runs/<timestamp>/`: `candidates.json`, `ranked.json`, `packets/*.md`.
3. Report: the scan line (files, candidates), the top 10 of `ranked.json` as a table (id, scanner, sites, lines_saved, score, policy), and the packet directory path.
4. Do not judge here. Judging is the `morphsaver-judge` skill; executing is `morphsaver-execute`.
5. If a `.morphsaver/policy.toml` is missing, say so and use defaults; do not write one without being asked.
6. Resume: `morphsaver rank <repo>` and `morphsaver packet <repo>` re-run on the newest run directory.
