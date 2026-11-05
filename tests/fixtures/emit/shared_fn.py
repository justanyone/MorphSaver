# True positive: clump and dispatch share handle() in this file.
def handle(kind, host, port, user):
    if kind == "a":
        return host + str(port) + user
    elif kind == "b":
        return user + host
    return ""


# Known false positive: same parameter names, different function, no shared site.
def other(host, port, user):
    return f"{host}:{port}@{user}"


__all__ = ["handle", "other"]  # both functions are scanner inputs, not callers
