"""repeated_dispatch: dispatch_chain candidates in different places that compare the same value set.

Not built yet beyond grouping by exact value set (the prototype rule). The ticket adds Jaccard matching and enum resolution.
Runs once over all per-file candidates; see scanners.__init__.CROSS_FILE.
"""
from __future__ import annotations

import collections
import hashlib

from ..model import Candidate

NAME = "repeated_dispatch"


def scan_all(candidates: list[Candidate], policy) -> list[Candidate]:
    groups: dict[tuple[str, ...], list[Candidate]] = collections.defaultdict(list)
    for c in candidates:
        if c.scanner == "dispatch_chain" and c.values:
            groups[tuple(sorted(set(c.values)))].append(c)
    found = []
    for values, members in groups.items():
        if len(members) < policy.min_sites:
            continue
        sites = [s for m in members for s in m.sites]
        digest = hashlib.sha1("|".join(values).encode()).hexdigest()[:10]
        policy_level = max((m.policy for m in members), key=("none", "caution", "deny").index)
        found.append(Candidate(f"{NAME}-{digest}", NAME, sites, members[0].discriminator_kind, values,
                               shape="strategy-classes", policy=policy_level))
    return found
