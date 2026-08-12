class ContinuousBatcher:
    def __init__(self):
        self.queue = []

    def add(self, request):
        self.queue.append(request)

    def flush(self):
        batch = self.queue
        self.queue = []
        return batch
