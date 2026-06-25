class Worker:
    def __init__(self, worker_id):
        self.worker_id = worker_id

    def execute(self, task):
        return {
            "worker": self.worker_id,
            "result": f"processed {task}"
        }
