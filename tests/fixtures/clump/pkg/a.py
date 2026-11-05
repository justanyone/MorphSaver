def connect(host, port, token):  # noqa: vulture
    client = (host, port)
    return client, token


def ping(host, port, token):  # noqa: vulture
    return host, port, token


def login(host, port, token, user):  # noqa: vulture
    return user, host, port, token
