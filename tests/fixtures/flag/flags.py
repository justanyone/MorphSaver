"""Fixture for flag_argument. Each function name says what the scanner must do."""

__all__ = ["report", "run", "forward", "once"]


def report(items, verbose: bool):
    # True positive: `verbose` is the whole test of two top-level ifs.
    if verbose:
        print("start")
    total = len(items)
    if not verbose:
        total = -1
    return total


def run(items, strict=False):
    # True positive: a default-False flag tested in two places (one with `not`).
    if strict:
        items.sort()
    if not strict:
        items.reverse()
    return items


def forward(items, verbose: bool):
    # False positive: the flag is only passed through to another call.
    return report(items, verbose)


def once(items, verbose: bool):
    # Flag tested once: not reported.
    if verbose:
        print("only once")
    return items
