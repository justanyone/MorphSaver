from enum import Enum


class Kind(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


def render(kind):
    if kind == Kind.A:
        return 0
    elif kind == Kind.B:
        return 1
    elif kind == Kind.C:
        return 2
    elif kind == Kind.D:
        return 3
