def area(kind, size):
    if kind == "circle":
        return 3.14 * size * size
    elif kind == "square":
        return size * size
    elif kind == "triangle":
        return size * size / 2
