"""Candidate records shared by every pipeline step. One JSON file per step; see docs/design/architecture.md.

Schema version lives in morphsaver.SCHEMA_VERSION. A reader refuses a file whose version it does not know.
"""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import SCHEMA_VERSION

SHAPES = ("dict-table", "strategy-classes", "template-method", "dataclass-param", "split-function")
VERDICTS = ("accept", "dict-table", "reject", "ask-owner")
POLICIES = ("none", "caution", "deny")


@dataclass(frozen=True)
class Site:
    """One place in the code that a candidate covers: a dispatch chain, a function in a parallel family, a call."""
    file: str
    line: int
    end_line: int
    function: str
    arms: int = 0
    lines: int = 0
    discriminator: str = ""
    values: tuple[str, ...] = ()
    has_else: bool = False
    kind: str = ""


@dataclass
class Candidate:
    """One refactoring opportunity. `id` is stable across runs: scanner + sha of (file, function, discriminator) of the sites."""
    id: str
    scanner: str
    sites: list[Site]
    discriminator_kind: str = ""          # literal-set | enum | type | flag | mixed
    values: tuple[str, ...] = ()          # union of site values, normalised
    shape: str = "dict-table"             # one of SHAPES; rank may change it; judge may change it
    policy: str = "none"                  # one of POLICIES, from policy.toml globs
    # filled by rank
    dup_lines: int = 0
    overhead_lines: int = 0
    lines_saved: int = 0
    callers: int = -1                     # -1 = unknown (no CodeGraph)
    tests: list[str] = field(default_factory=list)
    hot: list[str] = field(default_factory=list)   # ruff/radon codes that hit the enclosing functions
    score: float = 0.0
    # filled by judge
    verdict: str = ""
    rationale: str = ""
    revised_lines_saved: int | None = None

    def to_json(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Candidate:
        sites = [Site(**{**s, "values": tuple(s.get("values", ()))}) for s in data.pop("sites")]
        data["values"] = tuple(data.get("values", ()))
        return cls(sites=sites, **data)


def write_file(path: Path, step: str, candidates: list[Candidate], extra: dict[str, Any] | None = None) -> None:
    payload = {"schema": SCHEMA_VERSION, "step": step, "count": len(candidates),
               "candidates": [c.to_json() for c in candidates], **(extra or {})}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def read_file(path: Path) -> tuple[list[Candidate], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA_VERSION:
        raise ValueError(f"{path}: schema {payload.get('schema')!r}, this MorphSaver reads {SCHEMA_VERSION}")
    candidates = [Candidate.from_json(c) for c in payload["candidates"]]
    meta = {k: v for k, v in payload.items() if k != "candidates"}
    return candidates, meta
