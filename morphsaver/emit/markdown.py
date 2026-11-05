"""markdown: one task file per accepted candidate. Deterministic text: same verdicts, byte-identical output."""
from __future__ import annotations

from pathlib import Path

from ..model import Candidate

NAME = "markdown"
ACCEPTED = {"accept", "dict-table"}


def task_text(c: Candidate) -> str:
    sites = "\n".join(f"- `{s.file}:{s.line}-{s.end_line}` `{s.function}` ({s.arms} arms on `{s.discriminator}`)" for s in c.sites)
    saved = c.revised_lines_saved if c.revised_lines_saved is not None else c.lines_saved
    first = c.sites[0]
    title = f"refactor: {first.file}:{first.function} dispatch on {first.discriminator} -> {c.shape}"
    tests = "\n".join(f"- `{t}`" for t in c.tests) or "- (no tests reference these functions; add one before refactoring)"
    return f"""# {title}

Candidate `{c.id}` from scanner `{c.scanner}`. Verdict: {c.verdict}. Estimated line delta: {-saved:+d}.

## Sites
{sites}

## Target shape
{c.shape}

## Rationale
{c.rationale or '(none recorded)'}

## Rules
- Behaviour-preserving. No feature change. Public names stay unless listed below.
- One site per commit when there are more than 3 sites.
- Tests that must stay green:
{tests}

## Acceptance criteria
- Every listed site is removed or reduced to one lookup.
- The listed tests pass; no new test is deleted or skipped.
- The line delta is reported in the commit message or pull request body.
- No new public symbols beyond the base class and the registry (or the table).
"""


def emit(candidates: list[Candidate], out_dir: Path, meta: dict) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for c in candidates:
        if c.verdict in ACCEPTED:
            path = out_dir / f"{c.id}.md"
            path.write_text(task_text(c), encoding="utf-8")
            written.append(path)
    return written
