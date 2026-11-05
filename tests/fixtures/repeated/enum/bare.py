from .enum import Kind

A, B, C, D = Kind


def describe(category):
    if category == A:
        return 0
    elif category == B:
        return 1
    elif category == C:
        return 2
    elif category == D:
        return 3


describe(A)
