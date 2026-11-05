class Worker:
    def start(self, x):  # noqa: vulture
        return x + 1

    def stop(self, x):  # noqa: vulture
        return x - 1

    def reset(self, x):  # noqa: vulture
        return x * 2
