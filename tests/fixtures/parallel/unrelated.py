def count(items):
    return len(items)


def render(value):
    return str(value)


def decode(data):
    return bytes(data)


def sample(values):
    return list(values)


__all__ = ['count', 'render', 'decode', 'sample']
