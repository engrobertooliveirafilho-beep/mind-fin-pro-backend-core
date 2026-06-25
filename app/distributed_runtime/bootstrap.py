from app.distributed_runtime.task_queue.queue import TaskQueue
from app.distributed_runtime.workers.worker import Worker
from app.distributed_runtime.scheduler.scheduler import Scheduler
from app.distributed_runtime.concurrency.controller import ConcurrencyController

class DistributedRuntime:
    def __init__(self):
        self.queue = TaskQueue()
        self.workers = [Worker("A"), Worker("B"), Worker("C")]
        self.scheduler = Scheduler()
        self.concurrency = ConcurrencyController()

    def submit(self, task):
        self.queue.push(task)

    def run(self):
        task = self.queue.pop()

        if not task:
            return None

        worker = self.scheduler.assign(task, self.workers)
        locked = self.concurrency.lock(task)

        result = worker.execute(task)

        self.concurrency.unlock(task)

        return result
