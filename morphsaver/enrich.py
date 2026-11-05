"""Optional, read-only evidence for rank. No tool is required."""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .policy import SKIP_DIRS, Policy, match


def _read_tree(path: Path):
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None


def _local_path(target: Path, filename: str) -> Path | None:
    path = (target / filename).resolve()
    return path if path.is_relative_to(target) else None


def _functions(target, candidates):
    trees = {}
    spans = {}
    for c in candidates:
        for site in c.sites:
            if site.file not in trees:
                path = _local_path(target, site.file)
                trees[site.file] = _read_tree(path) if path else None
            tree = trees[site.file]
            nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and n.name == site.function.rsplit(".", 1)[-1]
                     and n.lineno <= site.line <= n.end_lineno] if tree else []
            if nodes:
                node = min(nodes, key=lambda n: n.end_lineno - n.lineno)
                spans[(site.file, site.function, site.line)] = (node.lineno, node.end_lineno)
    return spans


def _test_references(target: Path, policy: Policy):
    references = []
    for path in sorted(target.rglob("*.py")):
        rel = path.relative_to(target).as_posix()
        if any(part in SKIP_DIRS for part in path.relative_to(target).parts):
            continue
        if not any(match(rel, glob) for glob in policy.exclude) or not _local_path(target, rel):
            continue
        tree = _read_tree(path)
        if tree is None:
            continue
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.alias):
                names.add(node.name.rsplit(".", 1)[-1])
        references.append((rel, names))
    return references


def _ruff(stdout, target):
    data = json.loads(stdout)
    if not isinstance(data, list):
        raise TypeError("expected diagnostics")
    hits = []
    for item in data:
        if not isinstance(item, dict) or item.get("code") not in {"C901", "PLR0912", "PLR0911"}:
            continue
        filename, location = item.get("filename"), item.get("location")
        if not isinstance(filename, str) or not isinstance(location, dict):
            continue
        path = _local_path(target, filename)
        row = location.get("row")
        if path and type(row) is int and row > 0:
            hits.append((path.relative_to(target).as_posix(), row, item["code"]))
    return hits


def _radon(stdout, target):
    data = json.loads(stdout)
    if not isinstance(data, dict):
        raise TypeError("expected complexity blocks")
    hits = []

    def blocks(items, rel):
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            row, letter = item.get("lineno"), item.get("rank")
            if item.get("type") != "class" and type(row) is int and row > 0 and letter in tuple("ABCDEF"):
                hits.append((rel, row, "radon:" + letter))
            blocks(item.get("methods", []), rel)
            blocks(item.get("closures", []), rel)

    for filename, items in data.items():
        path = _local_path(target, filename)
        if path:
            blocks(items, path.relative_to(target).as_posix())
    return hits


def _caller_count(stdout):
    # CodeGraph's node command prints a Markdown trail of file:line references.
    trail = re.search(r"\*\*Called by ←\*\*([^\n]*)", stdout)
    if trail:
        return len(set(re.findall(r"\(([^()]+:\d+)\)", trail[1])))
    if "**Location:**" in stdout:
        return 0
    raise ValueError("expected a CodeGraph node")


def _hot_codes(candidate, spans, hits):
    hot = set()
    for site in candidate.sites:
        span = spans.get((site.file, site.function, site.line))
        if span:
            hot.update(code for rel, row, code in hits if rel == site.file and span[0] <= row <= span[1])
    return sorted(hot)


def _candidate_callers(candidate, callers, run, target):
    counts = {}
    for site in candidate.sites:
        if site.function == "<module>":
            continue
        key = (site.file, site.function)
        if key not in callers:
            callers[key] = run("codegraph", ["node", site.function, "--path", str(target), "--file", site.file],
                               _caller_count)
        if callers[key] is not None:
            counts[key] = callers[key]
    return sum(counts.values()) if counts else -1


def _apply_evidence(candidates, spans, references, hits, run, target):
    callers = {}
    for candidate in candidates:
        names = {s.function.rsplit(".", 1)[-1] for s in candidate.sites if s.function != "<module>"}
        candidate.tests = sorted({rel for rel, refs in references if names & refs})
        candidate.hot = _hot_codes(candidate, spans, hits)
        candidate.callers = _candidate_callers(candidate, callers, run, target)


def enrich(candidates, policy: Policy, target: Path) -> None:
    target = target.resolve()
    spans = _functions(target, candidates)
    references = _test_references(target, policy)
    executables = {tool: shutil.which(tool) for tool in ("ruff", "radon", "codegraph")}
    warned = set()

    def warning(tool, reason):
        if tool not in warned:
            print(f"warning: {tool}: {reason}; enrichment skipped", file=sys.stderr)
            warned.add(tool)

    def run(tool, args, parse):
        if not executables[tool]:
            return None
        try:
            result = subprocess.run([executables[tool], *args], cwd=target, capture_output=True,
                                    text=True, check=False, timeout=30)
            if result.returncode not in ((0, 1) if tool == "ruff" else (0,)):
                raise ValueError("tool failed")
            return parse(result.stdout)
        except (OSError, subprocess.SubprocessError, ValueError, TypeError, RecursionError):
            warning(tool, "unavailable or invalid output")
            return None

    for tool, executable in executables.items():
        if not executable:
            warning(tool, "not installed")
    hits = []
    hits.extend(run("ruff", ["check", "--select", "C901,PLR0912,PLR0911", "--output-format", "json", str(target)],
                    lambda out: _ruff(out, target)) or [])
    hits.extend(run("radon", ["cc", "-j", str(target)], lambda out: _radon(out, target)) or [])
    _apply_evidence(candidates, spans, references, hits, run, target)
