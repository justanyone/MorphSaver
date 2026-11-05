from .second import decode as decoder


def render(value):
    result = str(value)
    return result


def encode(value):
    result = bytes(value)
    return result


HANDLERS = {"a": render, "b": encode, "c": decoder}


__all__ = ['HANDLERS']
