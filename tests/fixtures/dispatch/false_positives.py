"""Fixture: shapes that look like dispatch chains but are not. The default policy must find zero candidates."""


def mixed_subjects(a, b):  # arms test different subjects
    if a == 1:
        return 1
    elif b == 2:
        return 2
    elif a == 3:
        return 3


def two_arms(kind):  # below min_arms (default 3)
    if kind == "a":
        return 1
    elif kind == "b":
        return 2


def guard_ladder(a, b, c):  # sequential `if` guards, not an elif chain
    if not a:
        return 1
    if not b:
        return 2
    if not c:
        return 3
    return 4


def nested_in_arm(kind, x):  # outer chain mixes subjects; inner chain has only two arms
    if kind == "a":
        if x == 1:
            return 1
        elif x == 2:
            return 2
        return 0
    elif kind == "b":
        return 2
    elif x == 3:
        return 3
