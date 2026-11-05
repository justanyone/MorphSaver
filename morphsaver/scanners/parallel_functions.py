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


def _module_names(rel: str) -> tuple[str, str]:
    path = PurePosixPath(rel)
    module = ".".join(path.with_suffix("").parts)
    package = module.rsplit(".", 1)[0] if path.parent != PurePosixPath(".") else ""
    return (package if path.stem == "__init__" else module), package


def _import_base(node: ast.ImportFrom, package: str) -> str:
    base = node.module or ""
    if node.level:
        parts = package.split(".")
        base = ".".join(parts[:len(parts) - node.level + 1] + ([base] if base else []))
    return base


def _import_aliases(tree, package: str) -> dict[str, str]:
    aliases = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            base = _import_base(node, package)
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{base}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                aliases[alias.asname or root] = alias.name if alias.asname else root
    return aliases


def _function_record(node: ast.FunctionDef | ast.AsyncFunctionDef, rel: str, name: str) -> Function:
    skeleton = tuple(type(n).__name__ for stmt in node.body for n in ast.walk(stmt))
    end_line = node.end_lineno or node.body[-1].end_lineno or node.body[-1].lineno
    site = Site(rel, node.lineno, end_line, name, arms=1,
                lines=end_line - node.body[0].lineno + 1,
                discriminator="family", kind="function")
    return Function(site, node.name, skeleton)


def _functions(node, rel: str, scope: str = ""):
    for child in ast.iter_child_nodes(node):
        name = scope
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{scope}.{child.name}" if scope else child.name
            if not isinstance(child, ast.ClassDef):
                yield _function_record(child, rel, name)
        yield from _functions(child, rel, name)


def _reference(node, module: str, aliases: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, f"{module}.{node.id}")
    if isinstance(node, ast.Attribute):
        base = _reference(node.value, module, aliases)
        return f"{base}.{node.attr}" if base else ""
    return ""


def _tables(tree, module: str, aliases: dict[str, str]):
    # Function-local names can shadow imports. Only module tables establish affinity.
    for statement in tree.body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)) and isinstance(statement.value, ast.Dict):
            yield tuple(sorted({ref for value in statement.value.values
                                if (ref := _reference(value, module, aliases))}))


def collect(tree, rel: str, policy) -> Records:
    """Return a per-file side output. References use absolute module names."""
    module, package = _module_names(rel)
    aliases = _import_aliases(tree, package)
    return Records(rel, tuple(_functions(tree, rel)), tuple(_tables(tree, module, aliases)))


def scan(tree, rel: str, policy) -> list[Candidate]:
    """Keep the per-file scanner interface for callers that scan one module."""
    return scan_all([collect(tree, rel, policy)], policy)


def _index_functions(files):
    functions = {}
    references = {}
    buckets = defaultdict(set)
    for rel, record in sorted(files.items()):
        module, _ = _module_names(rel)
        parent = str(PurePosixPath(rel).parent)
        # Root modules share no package. A directory defines one scan-local package.
        scope = parent if parent != "." else rel
        for function in record.functions:
            key = (rel, function.site.function)
            functions[key] = function
            references[f"{module}.{function.site.function}"] = key
            if len(function.name) >= 4:
                buckets[(scope, "prefix", function.name[:4])].add(key)
                buckets[(scope, "suffix", function.name[-4:])].add(key)
    return functions, references, buckets


def _add_table_buckets(files, references, buckets):
    for rel, record in sorted(files.items()):
        parent = PurePosixPath(rel).parent
        for index, table in enumerate(record.tables):
            for ref in table:
                key = references.get(ref)
                if key and (key[0] == rel or (str(parent) != "." and PurePosixPath(key[0]).parent == parent)):
                    buckets[(rel, "table", str(index))].add(key)


def _similarity_test(threshold: float):
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

    return similar


def _cluster_members(members, functions, similar):
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
            clusters.append(([skeleton], keys.copy()))
    return (tuple(sorted(cluster)) for _, cluster in clusters if len(cluster) >= 3)


def _candidate(sites: list[Site], policy) -> Candidate:
    identity = json.dumps([(s.file, s.function, s.discriminator) for s in sites])
    digest = hashlib.sha256(identity.encode()).hexdigest()[:16]
    levels = {"none": 0, "caution": 1, "deny": 2}
    level = max((policy.path_policy(s.file) for s in sites), key=levels.__getitem__)
    return Candidate(f"{NAME}-{digest}", NAME, sites, discriminator_kind="family",
                     shape="template-method", policy=level)


def _candidates(groups, functions, policy) -> list[Candidate]:
    found = []
    covering = defaultdict(list)
    for group in sorted(groups, key=lambda g: (-len(g), g)):
        members = frozenset(group)
        if any(members <= other for other in covering[group[0]]):
            continue
        for key in group:
            covering[key].append(members)
        found.append(_candidate([functions[key].site for key in group], policy))
    return found


def scan_all(records: list[Records], policy) -> list[Candidate]:
    """Group by affinity, then require pairwise skeleton similarity within each group."""
    threshold = policy.skeleton_similarity
    if not 0 <= threshold <= 1:
        raise ValueError("skeleton_similarity must be between 0 and 1")
    files = {r.file: r for r in records}
    functions, references, buckets = _index_functions(files)
    _add_table_buckets(files, references, buckets)
    similar = _similarity_test(threshold)
    groups = set()
    for members in buckets.values():
        if len(members) >= 3:
            groups.update(_cluster_members(members, functions, similar))
    return _candidates(groups, functions, policy)
