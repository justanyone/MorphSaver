"""flag_argument: not built yet. See docs/tasks.md for the ticket that builds it and docs/design/architecture.md for its rule."""
from __future__ import annotations

from ..model import Candidate

NAME = "flag_argument"


def scan(tree, rel: str, policy) -> list[Candidate]:
    return []
