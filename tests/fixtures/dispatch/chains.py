"""Fixture: six chain shapes. The dispatch_chain scanner must find exactly the ones marked FOUND."""
from enum import Enum


class Kind(Enum):
    A = 1
    B = 2
    C = 3


def literal_chain(kind):  # FOUND: literal-set, 4 arms, else
    if kind == "a":
        return 1
    elif kind == "b":
        return 2
    elif kind == "c":
        return 3
    elif kind == "d":
        return 4
    else:
        return 0


def enum_chain(kind):  # FOUND: enum, 3 arms
    if kind == Kind.A:
        return 1
    elif kind == Kind.B:
        return 2
    elif kind == Kind.C:
        return 3


def type_chain(node):  # FOUND: type, 3 arms
    if isinstance(node, dict):
        return "d"
    elif isinstance(node, list):
        return "l"
    elif isinstance(node, str):
        return "s"


def match_chain(kind):  # FOUND: match, 3 cases
    match kind:
        case "a":
            return 1
        case "b":
            return 2
        case _:
            return 0


def set_membership(kind):  # FOUND: literal-set with `in`, 3 arms
    if kind in ("a", "b"):
        return 1
    elif kind in {"c"}:
        return 2
    elif kind == "d":
        return 3


def two_arms(kind):  # not found: below min_arms
    if kind == "a":
        return 1
    elif kind == "b":
        return 2


def mixed_subjects(a, b):  # not found: arms test different subjects
    if a == 1:
        return 1
    elif b == 2:
        return 2
    elif a == 3:
        return 3
