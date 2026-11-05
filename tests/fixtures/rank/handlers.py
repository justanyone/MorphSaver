def handle(kind):
    if kind == "a":
        return 1
    elif kind == "b":
        return 2
    elif kind == "c":
        return 3


# Known false positive for test references: no test calls this function.
def untouched(kind):
    if kind == "x":
        return 4
    elif kind == "y":
        return 5
    elif kind == "z":
        return 6
