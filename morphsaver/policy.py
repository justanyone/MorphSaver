"""policy.toml: per-target thresholds, weights and path policy. Lives in <target>/.morphsaver/policy.toml.

Every key has a default, so a target with no policy file scans with the defaults. Nothing is denied by default.
"""
from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

STATE_DIR = ".morphsaver"
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".morphsaver", "dist", "build", ".tox", ".mypy_cache"}


@dataclass
class Policy:
    min_arms: int = 3
    min_sites: int = 2
    jaccard: float = 0.6
    skeleton_similarity: float = 0.8
    top: int = 25
    packet_max_lines: int = 400
    class_overhead: int = 4
    base_overhead: int = 6
    sites_weight: float = 1.5
    site_bonus: float = 2.0
    hot_bonus: float = 3.0
    risk_weight: float = 0.2
    no_tests_penalty: float = 10.0
    include: list[str] = field(default_factory=lambda: ["**/*.py"])
    exclude: list[str] = field(default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py"])
    deny: list[str] = field(default_factory=list)
    caution: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, target: Path) -> Policy:
        path = target / STATE_DIR / "policy.toml"
        if not path.is_file():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        flat = {**data.get("thresholds", {}), **data.get("weights", {}), **data.get("paths", {})}
        known = {k: v for k, v in flat.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def path_policy(self, rel: str) -> str:
        if any(match(rel, g) for g in self.deny):
            return "deny"
        if any(match(rel, g) for g in self.caution):
            return "caution"
        return "none"

    def wants(self, rel: str) -> bool:
        return any(match(rel, g) for g in self.include) and not any(match(rel, g) for g in self.exclude)


def match(rel: str, glob: str) -> bool:
    """fnmatch where a leading `**/` also matches a path with no directory part, so `**/*.py` matches `a.py`."""
    if fnmatch.fnmatch(rel, glob):
        return True
    return glob.startswith("**/") and fnmatch.fnmatch(rel, glob[3:])


def iter_files(target: Path, policy: Policy):
    """Yield (absolute path, relative posix path) for every file the policy includes."""
    for path in sorted(target.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(target).parts):
            continue
        rel = path.relative_to(target).as_posix()
        if policy.wants(rel):
            yield path, rel
