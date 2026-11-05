def sync(host, port, token):  # noqa: vulture
    return host, port, token


def stop(port, host, token):  # noqa: vulture
    return port, len(host), len(token)
