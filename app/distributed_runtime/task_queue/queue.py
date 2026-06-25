class TaskQueue:
    def __init__(self):
        self.queue = []

    def push(self, task):
        self.queue.append(task)

    def pop(self):
        return self.queue.pop(0) if self.queue else None
