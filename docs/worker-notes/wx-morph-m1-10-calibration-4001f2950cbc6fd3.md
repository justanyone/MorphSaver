# Calibration worker notes

- Read the ticket, design, policy defaults, and judge rules.
- Check for two local Python repositories above 250,000 lines.
- Keep all output in this worktree. Do not change scanner code.
- Retain defaults unless measured packet judgments support a change.
- Run offline focused tests and the final gate. Record missing inputs.
- Found three large local trees. Check repository identity before selecting two. The CLI writes into its target, so use worktree-local copies.
- Selected two distinct local projects. Copied Python source only to ignored worktree-local calibration inputs. No external writes. Next: scan and time each pipeline step.
- Focused offline checks passed: 35 rank and CLI tests. Repo A src alone is below the line limit; include tests and scripts in the input count, while the default scan policy excludes tests. Full top-25 runs are in progress.
- Fixture baseline: 26 files in 0.051 s; dispatch_chain 20, repeated_dispatch 4, parallel_functions 2, data_clump 2, flag_argument 2. Large scan is still running; no threshold evidence yet.
- 2026-11-05T06:37:16Z launcher: no commit for 60 s; 270 s elapsed. Files changed so far: .codegraph/.gitignore, docs/calibration.md, docs/worker-notes/wx-morph-m1-10-calibration-4001f2950cbc6fd3.md.
- Repo A has not produced scan output after several minutes. Started an independent 180 s bounded run on repo B so both inputs get an attempt. Preserve absent precision as unmeasured, not zero.
- Started the final offline gate. Both large scan attempts still lack candidate output. No scanner or policy default changed.
