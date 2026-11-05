"""Group dispatch chains connected by normalised value-set Jaccard overlap.

Runs once over all per-file candidates; see scanners.__init__.CROSS_FILE.
"""
from __future__ import annotations

import collections
import hashlib
import json

from ..model import Candidate

NAME = "repeated_dispatch"


def scan_all(candidates: list[Candidate], policy) -> list[Candidate]:
    """Join matching pairs transitively, independent of file and input order."""
    if not 0 <= policy.jaccard <= 1:
        raise ValueError("jaccard must be between 0 and 1")
    # dispatch_chain already normalises enum attributes, bare names, and literals.
    groups: dict[tuple[str, ...], dict[str, Candidate]] = collections.defaultdict(dict)
    for candidate in candidates:
        if candidate.scanner == "dispatch_chain" and candidate.values:
            groups[tuple(sorted(set(candidate.values)))][candidate.id] = candidate
    keys = sorted(groups)
    values = [set(key) for key in keys]
    parents = list(range(len(keys)))

    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for i, left in enumerate(values):
        for j in range(i + 1, len(values)):
            right = values[j]
            if len(left & right) / len(left | right) >= policy.jaccard:
                parents[root(j)] = root(i)
    components: dict[int, list[Candidate]] = collections.defaultdict(list)
    for i, key in enumerate(keys):
        components[root(i)].extend(groups[key].values())
    found = []
    for members in components.values():
        sites = sorted({s for m in members for s in m.sites},
                       key=lambda s: (s.file, s.function, s.discriminator, s.line))
        if len(sites) < policy.min_sites:
            continue
        union = tuple(sorted({value for m in members for value in m.values}))
        digest = hashlib.sha1(json.dumps(union).encode()).hexdigest()[:10]
        policy_level = max((m.policy for m in members), key=("none", "caution", "deny").index)
        kinds = {m.discriminator_kind for m in members}
        kind = next(iter(kinds)) if len(kinds) == 1 else "mixed"
        found.append(Candidate(f"{NAME}-{digest}", NAME, sites, kind, union,
                               shape="strategy-classes", policy=policy_level))
    return sorted(found, key=lambda candidate: candidate.id)
