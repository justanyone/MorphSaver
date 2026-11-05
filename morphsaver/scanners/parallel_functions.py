"""Find package-local function families without retaining state between scans."""
from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import PurePosixPath

from ..model import Candidate, Site

NAME = "parallel_functions"


@dataclass(frozen=True)
class Function:
    site: Site
    name: str
    skeleton: tuple[str, ...]


@dataclass(frozen=True)
class Records:
    file: str
    functions: tuple[Function, ...]
    tables: tuple[tuple[str, ...], ...]


def collect(tree, rel: str, policy) -> Records:
    """Return a per-file side output. References use absolute module names."""
    path = PurePosixPath(rel)
    module = ".".join(path.with_suffix("").parts)
    package = module.rsplit(".", 1)[0] if path.parent != PurePosixPath(".") else ""
    if path.stem == "__init__":
        module = package
    aliases = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = module.split(".") if path.stem == "__init__" else package.split(".")
                base = ".".join(parts[:len(parts) - node.level + 1] + ([base] if base else []))
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{base}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name if alias.asname else alias.name.split(".")[0]

    functions = []

    def visit(node, scope=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{scope}.{child.name}" if scope else child.name
                if not isinstance(child, ast.ClassDef):
                    skeleton = tuple(type(n).__name__ for stmt in child.body for n in ast.walk(stmt))
                    site = Site(rel, child.lineno, child.end_lineno, name, arms=1,
                                lines=child.end_lineno - child.body[0].lineno + 1,
                                discriminator="family", kind="function")
                    functions.append(Function(site, child.name, skeleton))
                visit(child, name)
            else:
                visit(child, scope)

    visit(tree)

    def reference(node):
        if isinstance(node, ast.Name):
            return aliases.get(node.id, f"{module}.{node.id}")
        if isinstance(node, ast.Attribute):
            base = reference(node.value)
            return f"{base}.{node.attr}" if base else ""
        return ""

    # Only module-level tables establish affinity. Function-local names can shadow imports.
    tables = []
    for statement in tree.body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
            value = statement.value
            if isinstance(value, ast.Dict):
                tables.append(tuple(sorted({ref for v in value.values if (ref := reference(v))})))
    return Records(rel, tuple(functions), tuple(tables))


def scan(tree, rel: str, policy) -> list[Candidate]:
    """Keep the per-file scanner interface for callers that scan one module."""
    return scan_all([collect(tree, rel, policy)], policy)


def scan_all(records: list[Records], policy) -> list[Candidate]:
    """Group by affinity, then require pairwise skeleton similarity within each group."""
    threshold = policy.skeleton_similarity
    if not 0 <= threshold <= 1:
        raise ValueError("skeleton_similarity must be between 0 and 1")
    files = {r.file: r for r in records}
    functions = {}
    references = {}
    buckets = defaultdict(set)
    for rel, record in sorted(files.items()):
        path = PurePosixPath(rel)
        module = ".".join(path.with_suffix("").parts)
        if path.stem == "__init__":
            module = ".".join(path.parent.parts)
        # Root modules share no package. A directory defines one scan-local package.
        scope = str(path.parent) if str(path.parent) != "." else rel
        for function in record.functions:
            key = (rel, function.site.function)
            functions[key] = function
            references[f"{module}.{function.site.function}"] = key
            if len(function.name) >= 4:
                buckets[(scope, "prefix", function.name[:4])].add(key)
                buckets[(scope, "suffix", function.name[-4:])].add(key)
    for rel, record in sorted(files.items()):
        parent = PurePosixPath(rel).parent
        for index, table in enumerate(record.tables):
            for ref in table:
                key = references.get(ref)
                if key and (key[0] == rel or (str(parent) != "." and PurePosixPath(key[0]).parent == parent)):
                    buckets[(rel, "table", str(index))].add(key)

    similarities = {}

    def similar(left, right):
        if left == right:
            return True
        pair = tuple(sorted((left, right)))
        if pair not in similarities:
            matcher = SequenceMatcher(None, left, right, autojunk=False)
            similarities[pair] = (matcher.real_quick_ratio() >= threshold
                                  and matcher.quick_ratio() >= threshold
                                  and matcher.ratio() >= threshold)
        return similarities[pair]

    groups = set()
    for members in buckets.values():
        if len(members) < 3:
            continue
        by_skeleton = defaultdict(set)
        for key in sorted(members):
            by_skeleton[functions[key].skeleton].add(key)
        clusters = []
        for skeleton, keys in by_skeleton.items():
            for shapes, cluster in clusters:
                if all(similar(skeleton, shape) for shape in shapes):
                    shapes.append(skeleton)
                    cluster.update(keys)
                    break
            else:
                clusters.append(([skeleton], set(keys)))
        groups.update(tuple(sorted(cluster)) for _, cluster in clusters if len(cluster) >= 3)

    found = []
    covering = defaultdict(list)
    for group in sorted(groups, key=lambda g: (-len(g), g)):
        members = frozenset(group)
        if any(members <= other for other in covering[group[0]]):
            continue
        for key in group:
            covering[key].append(members)
        sites = [functions[key].site for key in group]
        identity = json.dumps([(s.file, s.function, s.discriminator) for s in sites])
        digest = hashlib.sha256(identity.encode()).hexdigest()[:16]
        level = max((policy.path_policy(s.file) for s in sites), key={"none": 0, "caution": 1, "deny": 2}.get)
        found.append(Candidate(f"{NAME}-{digest}", NAME, sites, discriminator_kind="family",
                               shape="template-method", policy=level))
    return found
