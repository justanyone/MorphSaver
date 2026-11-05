__all__ = ["connect", "login", "ping"]


def connect(host, port, token):
    client = (host, port)
    return client, token


def ping(host, port, token):
    return host, port, token


def login(host, port, token, user):
    return user, host, port, token
