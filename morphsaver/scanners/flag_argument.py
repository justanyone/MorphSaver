"""flag_argument: a boolean parameter that is the whole test of an if at the top of a function body, in two or more places.

A parameter counts as a flag when it is annotated `bool` or defaults to `True` or `False`. A test counts when it is
the bare name (`if verbose:`) or its negation (`if not verbose:`), at the top level of the body or in its elif chain.
Passing the flag on to another call is not a test. Candidate id: hash of (file, function, flag name), never a line.
"""
from __future__ import annotations

import ast

from ..model import Candidate, Site
from . import dispatch_chain

NAME = "flag_argument"
MIN_TESTS = 2


def candidate_id(rel: str, function: str, flag: str) -> str:
    """Same stable hash as dispatch_chain.candidate_id, with this scanner's prefix."""
    return dispatch_chain.candidate_id(rel, function, flag).replace(dispatch_chain.NAME, NAME, 1)


def _is_bool_annotation(ann) -> bool:
    return (isinstance(ann, ast.Name) and ann.id == "bool") or (
        isinstance(ann, ast.Constant) and ann.value == "bool")


def _is_bool_default(default) -> bool:
    return isinstance(default, ast.Constant) and isinstance(default.value, bool)


def flag_params(fn) -> list[str]:
    """Names of the parameters of `fn` that are bool-typed or bool-defaulted, in source order."""
    pos = fn.args.posonlyargs + fn.args.args
    defaults = [None] * (len(pos) - len(fn.args.defaults)) + list(fn.args.defaults)
    pairs = list(zip(pos, defaults)) + list(zip(fn.args.kwonlyargs, fn.args.kw_defaults))
    return [a.arg for a, d in pairs if _is_bool_annotation(a.annotation) or _is_bool_default(d)]


def _tests(test, flag: str) -> bool:
    if isinstance(test, ast.Name):
        return test.id == flag
    return isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and _tests(test.operand, flag)


def count_tests(fn, flag: str) -> int:
    """How many top-level if tests (own or in their elif chain) are the bare flag or `not flag`."""
    n = 0
    for stmt in fn.body:
        node = stmt
        while isinstance(node, ast.If):
            n += _tests(node.test, flag)
            node = node.orelse[0] if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If) else None
    return n


def scan(tree, rel: str, policy) -> list[Candidate]:
    found = []
    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for fn in sorted(functions, key=lambda n: (n.lineno, n.col_offset)):
        for flag in flag_params(fn):
            n = count_tests(fn, flag)
            if n < MIN_TESTS:
                continue
            end = fn.end_lineno or fn.lineno
            site = Site(rel, fn.lineno, end, fn.name, arms=n, lines=end - fn.lineno + 1,
                        discriminator=flag, values=(flag,), has_else=False, kind="if-flag")
            found.append(Candidate(candidate_id(rel, fn.name, flag), NAME, [site], "flag", (flag,),
                                   shape="split-function", policy=policy.path_policy(rel)))
    return found
