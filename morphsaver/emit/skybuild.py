"""skybuild: plugin emitter for a build factory that files tasks through an HTTP task service.

Not built yet. Rules for this file (ADR 0008): service URL, token path and project id come from environment variables
(MORPHSAVER_TASK_API, MORPHSAVER_TASK_TOKEN_FILE, MORPHSAVER_TASK_PROJECT). Nothing about any particular deployment is written here.
"""
from __future__ import annotations

from pathlib import Path

from ..model import Candidate

NAME = "skybuild"


def emit(candidates: list[Candidate], out_dir: Path, meta: dict) -> list[Path]:
    raise NotImplementedError("skybuild emitter: see docs/tasks.md")
