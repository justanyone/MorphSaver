"""Qualified enum names must join bare members and string literals."""

from . import enum as domain


def serialize(category):
    if category == domain.Kind.A:
        return 0
    elif category == domain.Kind.B:
        return 1
    elif category == domain.Kind.C:
        return 2
    elif category == domain.Kind.D:
        return 3
