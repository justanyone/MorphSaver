"""rank: the cost model. Deterministic: same candidates and policy give the same order.

lines_saved = dup_lines - overhead. Negative is reported, never hidden (ADR 0005).
A single-site candidate with lines_saved <= 0 keeps shape dict-table. Optional evidence is collected when a target is supplied.
"""
from __future__ import annotations

from pathlib import Path

from .enrich import enrich
from .model import Candidate
from .policy import Policy


def cost(c: Candidate, policy: Policy) -> None:
    arms = max((s.arms for s in c.sites), default=0)
    sites = len(c.sites)
    c.dup_lines = sum(s.lines for s in c.sites)
    if c.shape == "template-method":
        c.overhead_lines = policy.base_overhead + sites * policy.class_overhead
    else:
        c.overhead_lines = arms * policy.class_overhead + policy.base_overhead + arms
    c.lines_saved = c.dup_lines - c.overhead_lines
    if sites == 1 and c.lines_saved <= 0:
        c.shape = "dict-table"
    elif c.scanner in ("dispatch_chain", "repeated_dispatch"):
        c.shape = "strategy-classes"
    risk = max(c.callers, 0) * policy.risk_weight
    penalty = policy.no_tests_penalty if not c.tests else 0.0
    # sites_weight multiplies a positive saving only; a negative saving must not get worse for having more sites.
    # site_bonus rewards every extra site that collapses, whatever the sign, so repetition outranks a lone chain.
    gain = c.lines_saved * (policy.sites_weight if sites > 1 and c.lines_saved > 0 else 1.0)
    c.score = round(gain + policy.site_bonus * (sites - 1) + len(set(c.hot)) * policy.hot_bonus - risk - penalty, 2)


def rank(candidates: list[Candidate], policy: Policy, target: Path | None = None) -> list[Candidate]:
    if target is not None:
        enrich(candidates, policy, target)
    for c in candidates:
        cost(c, policy)
    return sorted(candidates, key=lambda c: (-c.score, -len(c.sites), c.id))
