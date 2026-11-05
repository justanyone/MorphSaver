---
name: morphsaver-execute
description: Execute one MorphSaver task file (a behaviour-preserving refactor to classes, a dispatch table or a dataclass). Use when handed a task from .morphsaver/runs/<run>/tasks/.
---

# MorphSaver execute

One task file, one branch. The task names the sites, the target shape, the tests that must stay green and the acceptance criteria.

1. Run the listed tests first. If any is red before you change anything, stop and report.
2. Build the new shape beside the old code (base class and registry, or the table). Move one site at a time; run the tests after each.
3. One site per commit when the task lists more than 3 sites.
4. Remove the old arms only when every site goes through the new shape.
5. Keep public names. Add no feature. Do not widen the task.
6. Report the signed line delta (`git diff --shortstat`) in the commit message or pull request body, with the task id.
7. If the refactor turns out to grow the code or the tests do not cover a site, stop and report `reject` with the reason rather than forcing it.
