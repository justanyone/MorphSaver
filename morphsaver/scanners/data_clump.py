"""data_clump: the same parameter names in several signatures, or the same dict keys read from one variable, in several functions.

Per file, `scan` emits fact candidates (scanner `data_clump`, discriminator_kind `fact`). `scan_all` groups the facts
(signatures per directory, keys per variable name) and reports each clump of >= 3 names in >= 4 functions.
The cli drops fact candidates after the cross-file pass. Names `self`, `cls` and single-letter names never count.
"""
from __future__ import annotations

import ast
import collections
import hashlib
import posixpath
from dataclasses import replace

from ..model import Candidate, Site

NAME = "data_clump"
MIN_NAMES = 3
MIN_SITES = 4
IGNORED = frozenset({"self", "cls"})
FACT = "fact"


def _params(fn) -> frozenset[str]:
    args = fn.args
    names = (a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs))
    return frozenset(n for n in names if n not in IGNORED and len(n) > 1)


def _body_lines(fn) -> int:
    body = fn.body
    return (body[-1].end_lineno or body[-1].lineno) - body[0].lineno + 1


def _keys(fn) -> dict[str, set[str]]:
    keys: dict[str, set[str]] = collections.defaultdict(set)
    for node in ast.walk(fn):
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)):
            keys[node.value.id].add(node.slice.value)
    return keys


def _fact(rel: str, fn, kind: str, discriminator: str, values: tuple[str, ...]) -> Candidate:
    site = Site(rel, fn.lineno, fn.end_lineno or fn.lineno, fn.name, 0, _body_lines(fn), discriminator, values, False, kind)
    return Candidate("", NAME, [site], FACT, values, shape="dataclass-param")


def scan(tree: ast.AST, rel: str, policy) -> list[Candidate]:
    facts = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names = _params(fn)
        if len(names) >= MIN_NAMES:
            facts.append(_fact(rel, fn, "signature", "signature", tuple(sorted(names))))
        for var, keys in sorted(_keys(fn).items()):
            usable = tuple(sorted(k for k in keys if len(k) > 1))
            if len(usable) >= MIN_NAMES:
                facts.append(_fact(rel, fn, "keys", f"keys:{var}", usable))
    return facts


def _clumps(entries, group: tuple[str, str], policy) -> list[Candidate]:
    # Candidate clump sets: each function's names and every pairwise overlap of >= MIN_NAMES names.
    sets = {s for _, s in entries}
    sets |= {a & b for i, (_, a) in enumerate(entries) for _, b in entries[i + 1:] if len(a & b) >= MIN_NAMES}
    by_set: dict[frozenset[str], tuple[Site, ...]] = {}
    for clump in sets:
        if len(clump) < MIN_NAMES:
            continue
        sites = tuple(sorted((site for site, s in entries if clump <= s), key=lambda x: (x.file, x.line, x.function)))
        if len(sites) >= MIN_SITES:
            by_set[clump] = sites
    # Drop a clump that is a strict subset of a bigger clump covering exactly the same sites.
    kept = [(c, sites) for c, sites in by_set.items() if not any(c < d and sites == by_set[d] for d in by_set)]
    out = []
    for clump, sites in sorted(kept, key=lambda k: (-len(k[0]), sorted(k[0]))):
        values = tuple(sorted(clump))
        digest = hashlib.sha1("|".join((*group, *values)).encode()).hexdigest()[:10]
        out.append(Candidate(f"{NAME}-{digest}", NAME, [replace(s, values=values) for s in sites], "clump", values,
                             shape="dataclass-param", policy=policy.path_policy(sites[0].file)))
    return out


def scan_all(candidates: list[Candidate], policy) -> list[Candidate]:
    groups: dict[tuple[str, str], list[tuple[Site, frozenset[str]]]] = collections.defaultdict(list)
    for c in candidates:
        if c.scanner != NAME or c.discriminator_kind != FACT or not c.sites:
            continue
        site = c.sites[0]
        group = ("signature", posixpath.dirname(site.file)) if site.kind == "signature" else ("keys", site.discriminator)
        groups[group].append((site, frozenset(c.values)))
    found = []
    for group in sorted(groups):
        found.extend(_clumps(groups[group], group, policy))
    return found
