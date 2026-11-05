__all__ = ["read_four", "read_one", "read_three", "read_two"]


def read_one(d):
    first = d["host"]
    return first, d["port"], d["token"]


def read_two(d):
    value = d["host"]
    return value, d["port"], d["token"]


def read_three(d):
    token = d["token"]
    host = d["host"]
    port = d["port"]
    return token, host, port, d[0]


def read_four(d):
    return {"h": d["host"], "p": d["port"], "t": d["token"]}
