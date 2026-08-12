class LifecycleEngine:
    def transition(self, job, state):
        job['status'] = state
        return job
