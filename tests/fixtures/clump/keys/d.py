def read_one(d):
    return d["host"], d["port"], d["token"]


def read_two(d):
    value = d["host"]
    return value, d["port"], d["token"]


def read_three(d):
    return d["token"], d["host"], d["port"], d[0]


def read_four(d):
    return {"h": d["host"], "p": d["port"], "t": d["token"]}
