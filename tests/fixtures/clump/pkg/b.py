__all__ = ["stop", "sync"]


def sync(host, port, token):
    return host, port, token


def stop(port, host, token):
    return port, len(host), len(token)
