---
name: close-pr
description: Safely close a MorphSaver pull request. For a standing development-cycle closeout, finish the merge and start the next cycle in this same workflow. Trigger on "Close-PR", "close PR", "close out a PR", "close a development branch/cycle", or "done and start-next".
---

# Close-PR (MorphSaver)

The same branch and pull-request pattern as every project the owner runs. Read `AGENTS.md` and this skill before acting.
Work only in a MorphSaver checkout; verify its root and that `origin` is `justanyone/MorphSaver` before any Git or GitHub write.

## Branch pattern

- `main` is release-only. Nothing lands on `main` except the merge of a standing development cycle.
- Each development cycle is a branch `dev-NNN` (three digits, sequential: `dev-001`, `dev-002`, ...), created from the exact
  `main` SHA the previous cycle merged. Its first commit holds exactly one new README line that records the cycle start.
- A standing pull request `dev-NNN -> main` is open for the whole cycle, titled `dev-NNN → main: [summary]`.
- Work lands on `dev-NNN` only through task pull requests, one per task branch, merged by the factory or by the owner after
  review and a green `tools/gate.sh`. Nobody pushes to `dev-NNN` or `main` by hand after the cycle-start commit.
- Task branches are named by the factory (`task/<key>-...`) or, by hand, `<kind>/<short-topic>`; they are deleted after merge.
- A cycle closes when the owner says so; a commit count is a scheduling signal, not approval.

## Establish the requested closeout

Identify the exact PR by number and head branch, never by title alone. For a cycle close, confirm the owner's stated
boundary and intended base. Record the PR number, head and base branch names and SHAs, state, mergeability, and the
requested outcome. If the PR or boundary is ambiguous, stop before writes and ask one focused question.

Fetch current refs; inspect `git status`, open PRs, worktrees, dependent PRs and the branch inventory. Preserve unrelated
dirty or untracked work. Confirm the head is the reviewed candidate and that `tools/gate.sh` passed on it (CI green on the
PR is the evidence for a task PR; a full local `tools/gate.sh` run on the head is required for the standing PR). Require
GitHub to report the PR open, clean and mergeable; investigate ahead or behind changes instead of trusting an old snapshot.

Before merge, post one concise PR comment: delivered features, limitations, validation evidence (gate output, calibration
numbers), known-bad or unresolved state. Use `gh pr comment <number> --body-file <file>`. A comment adds evidence; do not
rewrite the PR body silently.

## Merge and verify

- Task PR into `dev-NNN`: `gh pr merge <number> --merge --delete-branch` after review and green checks. No squash, no rebase.
- Standing `dev-NNN -> main` PR: run the full `tools/gate.sh` on the exact head, then `gh pr merge <number> --merge` when the
  owner authorized the close. Never squash or rebase the standing PR. Never bypass failed or stale checks or a ref race.
- After merge, verify: PR merged state, intended base, merge commit SHA, remote target SHA; the target contains the reviewed
  candidate and no unexpected commit. Record the evidence in the report. Merging is not releasing: a release is a tag
  `vX.Y.Z` on `main` plus the steps in `docs/release.md`, done only on the owner's word.

## Optional branch cleanup

Only when the owner requested closeout and the merge is verified. List branches with `git branch -r --merged origin/main`
and delete only branches that are merged and owned by no live worktree or open PR. Never force-delete, never widen the list.

## Start the next development cycle

Mandatory final phase of a standing `dev-NNN -> main` closeout; never run it for a task PR. From the exact merged `main`
SHA: `git checkout -b dev-MMM` (MMM = NNN + 1), add exactly one README line under "Development cycles" recording the new cycle
and date, `git diff --check`, commit, push, then `gh pr create --base main --head dev-MMM --title "dev-MMM → main: [summary]"`.
Leave it open. Tell the factory's project record the new base branch (the owner's step on the factory side). Report both the
completed merge and the new branch and PR.

## Report

PR number, exact head, base and merge commit, the comment posted, gate and review evidence, final target SHA, cleanup done,
remaining blockers. Distinguish merged, published, released and deployed.
