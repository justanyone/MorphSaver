"""dispatch_chain: an if/elif chain or `match` whose every arm tests the same discriminator.

Ported from the 2026-11-04 prototype. Records discriminator kind, arm values, arm body lines, and whether an else exists.
"""
from __future__ import annotations

import ast
import hashlib

from ..model import Candidate, Site

NAME = "dispatch_chain"


def unparse(node) -> str:
    try:
        return ast.unparse(node)
    except (ValueError, TypeError, AttributeError):  # pragma: no cover - defensive
        return "?"


def discriminator(test) -> tuple[str, str] | None:
    """(subject text, kind) of a comparison test, or None when the test is not a dispatch on one subject."""
    if (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is)
            and isinstance(test.left, ast.Call) and isinstance(test.left.func, ast.Name) and test.left.func.id == "type"
            and test.left.args):
        return "type(" + unparse(test.left.args[0]) + ")", "type"
    if isinstance(test, ast.Name):
        return test.id, "flag"
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and isinstance(test.operand, ast.Name):
        return test.operand.id, "flag"
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], (ast.Eq, ast.In, ast.Is, ast.NotEq)):
        comp = test.comparators[0]
        if isinstance(comp, ast.Constant):
            kind = "literal-set"
        elif isinstance(comp, ast.Attribute):
            kind = "enum"
        elif isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
            kind = "literal-set"
        else:
            kind = "mixed"
        return unparse(test.left), kind
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "isinstance" and test.args:
        return "isinstance(" + unparse(test.args[0]) + ")", "type"
    if (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is)
            and isinstance(test.left, ast.Call) and isinstance(test.left.func, ast.Name) and test.left.func.id == "type"):
        return "type(" + unparse(test.left.args[0]) + ")", "type"
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.Or):
        subs = {discriminator(v) for v in test.values}
        if len(subs) == 1:
            return subs.pop()
    return None


def arm_values(test) -> list[str]:
    if isinstance(test, ast.Name):
        return ["True"]
    if isinstance(test, ast.UnaryOp):
        return ["False"]
    if isinstance(test, ast.Compare):
        comp = test.comparators[0]
        if isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
            return [unparse(e) for e in comp.elts]
        return [unparse(comp)]
    if isinstance(test, ast.Call):
        return [unparse(a) for a in test.args[1:]]
    if isinstance(test, ast.BoolOp):
        return [v for sub in test.values for v in arm_values(sub)]
    return []


def walk_chain(node: ast.If):
    arms, cur = [], node
    while isinstance(cur, ast.If):
        arms.append(cur)
        if len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
            cur = cur.orelse[0]
        else:
            break
    has_else = bool(cur.orelse) and not (len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If))
    return arms, has_else, cur


def body_lines(arm) -> int:
    body = arm.body
    return (body[-1].end_lineno or body[-1].lineno) - body[0].lineno + 1


def normalise(value: str) -> str:
    """Strip quotes and a leading Enum class so 'a', "a" and Kind.A compare equal across sites."""
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v.rsplit(".", 1)[-1] if "." in v and v[0].isupper() else v


def candidate_id(rel: str, function: str, discriminator_text: str) -> str:
    digest = hashlib.sha1(f"{rel}|{function}|{discriminator_text}".encode()).hexdigest()[:10]
    return f"{NAME}-{digest}"


class _Visitor(ast.NodeVisitor):
    def __init__(self, rel: str, policy):
        self.rel, self.policy, self.function, self.seen, self.found = rel, policy, "<module>", set(), []

    def visit_FunctionDef(self, node):
        old, self.function = self.function, node.name
        self.generic_visit(node)
        self.function = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_If(self, node):
        if id(node) in self.seen:
            return self.generic_visit(node)
        arms, has_else, last = walk_chain(node)
        for arm in arms:
            self.seen.add(id(arm))
        discs = [discriminator(a.test) for a in arms]
        if len(arms) >= self.policy.min_arms and discs[0] and all(d == discs[0] for d in discs):
            text, kind = discs[0]
            values = tuple(normalise(v) for a in arms for v in arm_values(a.test))
            all_return = all(isinstance(a.body[-1], ast.Return) for a in arms)
            site = Site(self.rel, node.lineno, last.end_lineno or node.lineno, self.function, len(arms),
                        sum(body_lines(a) for a in arms), text, values, has_else, "if-elif", all_return=all_return)
            self.found.append(Candidate(candidate_id(self.rel, self.function, text), NAME, [site], kind, values,
                                        policy=self.policy.path_policy(self.rel)))
        self.generic_visit(node)

    def visit_Match(self, node):
        if len(node.cases) >= self.policy.min_arms:
            text = unparse(node.subject)
            values = tuple(normalise(unparse(c.pattern)) for c in node.cases)
            has_else = any(isinstance(c.pattern, ast.MatchAs) and c.pattern.pattern is None for c in node.cases)
            all_return = all(isinstance(c.body[-1], ast.Return) for c in node.cases)
            site = Site(self.rel, node.lineno, node.end_lineno or node.lineno, self.function, len(node.cases),
                        sum(body_lines(c) for c in node.cases), text, values, has_else, "match", all_return=all_return)
            self.found.append(Candidate(candidate_id(self.rel, self.function, text), NAME, [site], "mixed", values,
                                        policy=self.policy.path_policy(self.rel)))
        self.generic_visit(node)


def scan(tree: ast.AST, rel: str, policy) -> list[Candidate]:
    visitor = _Visitor(rel, policy)
    visitor.visit(tree)
    return visitor.found
