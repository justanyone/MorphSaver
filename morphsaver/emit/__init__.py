"""Emitters: turn judged candidates into tasks. Each module exposes NAME and emit(candidates, out_dir, meta) -> list[Path].

The core never mentions a host project. A host-specific emitter (for example a build factory) is a plugin module here
that reads its service address from the environment, never from this repository (ADR 0008).
"""
from . import github, markdown, skybuild

ALL = {m.NAME: m for m in (markdown, github, skybuild)}
