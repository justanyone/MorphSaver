"""github: issue bodies, one JSON per accepted candidate for `gh issue create --body-file`. Not built yet."""
from __future__ import annotations

from pathlib import Path

from ..model import Candidate

NAME = "github"


def emit(candidates: list[Candidate], out_dir: Path, meta: dict) -> list[Path]:
    raise NotImplementedError("github emitter: see docs/tasks.md")
