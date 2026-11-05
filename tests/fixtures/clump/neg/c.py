class Worker:
    def start(self, x):
        return x + 1

    def stop(self, x):
        return x - 1

    def reset(self, x):
        return x * 2


if __name__ == "__main__":
    w = Worker()
    print(w.start(1), w.stop(1), w.reset(1))
