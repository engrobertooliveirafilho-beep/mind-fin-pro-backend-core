class JobQueue:
    def __init__(self):
        self.jobs = []

    def submit(self, job):
        self.jobs.append(job)

    def next(self):
        return self.jobs.pop(0) if self.jobs else None
