class GlobalState:
    def __init__(self):
        self.jobs = {}

    def create_job(self, job_id, data):
        self.jobs[job_id] = {
            'status': 'queued',
            'data': data
        }

    def update(self, job_id, status):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = status
