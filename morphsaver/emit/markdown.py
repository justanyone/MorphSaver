"""markdown: one task file per accepted candidate. Deterministic text: same verdicts, byte-identical output."""
from __future__ import annotations

from pathlib import Path

from ..model import Candidate

NAME = "markdown"
__all__ = ["NAME", "depends_map", "emit", "readme_text", "task_text", "title_of"]  # NAME is read by emit/__init__.py
ACCEPTED = {"accept", "dict-table"}


POLY = {"dispatch_chain", "repeated_dispatch", "parallel_functions"}


def _fn_keys(c: Candidate) -> set[tuple[str, str]]:
    return {(s.file, s.function) for s in c.sites}


def depends_map(candidates: list[Candidate]) -> dict[str, list[str]]:
    """Polymorphism candidate id -> sorted clump ids that share a (file, function) with it."""
    accepted = [c for c in candidates if c.verdict in ACCEPTED]
    clumps = [c for c in accepted if c.scanner == "data_clump"]
    deps: dict[str, list[str]] = {}
    for poly in accepted:
        if poly.scanner not in POLY:
            continue
        keys = _fn_keys(poly)
        hits = sorted(c.id for c in clumps if _fn_keys(c) & keys)
        if hits:
            deps[poly.id] = hits
    return deps


def task_text(c: Candidate, deps: list[str] | None = None) -> str:
    sites = "\n".join(f"- `{s.file}:{s.line}-{s.end_line}` `{s.function}` ({s.arms} arms on `{s.discriminator}`)" for s in c.sites)
    saved = c.revised_lines_saved if c.revised_lines_saved is not None else c.lines_saved
    first = c.sites[0]
    title = f"refactor: {first.file}:{first.function} dispatch on {first.discriminator} -> {c.shape}"
    dep_line = "".join(f"depends_on: {d}\n" for d in (deps or []))
    tests = "\n".join(f"- `{t}`" for t in c.tests) or "- (no tests reference these functions; add one before refactoring)"
    return f"""# {title}
{dep_line}
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


def title_of(c: Candidate) -> str:
    first = c.sites[0]
    return f"refactor: {first.file}:{first.function} dispatch on {first.discriminator} -> {c.shape}"


def readme_text(accepted: list[Candidate], deps: dict[str, list[str]]) -> str:
    lines = ["# Tasks", "", "| Task | Title | Line delta | depends_on |", "| --- | --- | --- | --- |"]
    for c in sorted(accepted, key=lambda c: c.id):
        saved = c.revised_lines_saved if c.revised_lines_saved is not None else c.lines_saved
        dep = ", ".join(deps.get(c.id, [])) or "-"
        lines.append(f"| `{c.id}.md` | {title_of(c)} | {-saved:+d} | {dep} |")
    return "\n".join(lines) + "\n"


def _write_if_changed(path: Path, text: str, written: list[Path]) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8")
    written.append(path)


def emit(candidates: list[Candidate], out_dir: Path, meta: dict) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    accepted = [c for c in candidates if c.verdict in ACCEPTED]
    deps = depends_map(candidates)
    for c in accepted:
        _write_if_changed(out_dir / f"{c.id}.md", task_text(c, deps.get(c.id)), written)
    _write_if_changed(out_dir / "README.md", readme_text(accepted, deps), written)
    return written
