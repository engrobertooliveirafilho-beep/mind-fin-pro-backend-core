class SharedMemoryField:
    def __init__(self):
        self.global_memory = []

    def write(self, event):
        self.global_memory.append(event)
