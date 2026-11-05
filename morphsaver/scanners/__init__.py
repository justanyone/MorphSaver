"""Scanner registry. A scanner is a module with `NAME` and `scan(tree, rel_path, policy) -> list[Candidate]`.

The tree is a Python `ast` module in v1. ADR 0009 keeps this interface so a tree-sitter backend can be added per language.
"""
from __future__ import annotations

from . import data_clump, dispatch_chain, flag_argument, parallel_functions, repeated_dispatch

PER_FILE = (dispatch_chain, data_clump, flag_argument)   # run on each file's tree
CROSS_FILE = (repeated_dispatch, parallel_functions,)                                            # run once over all per-file candidates
ALL = {m.NAME: m for m in PER_FILE + CROSS_FILE}
