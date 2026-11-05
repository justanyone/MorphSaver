def read_one(d):  # noqa: vulture
    first = d["host"]
    return first, d["port"], d["token"]


def read_two(d):  # noqa: vulture
    value = d["host"]
    return value, d["port"], d["token"]


def read_three(d):  # noqa: vulture
    token = d["token"]
    host = d["host"]
    port = d["port"]
    return token, host, port, d[0]


def read_four(d):  # noqa: vulture
    return {"h": d["host"], "p": d["port"], "t": d["token"]}
