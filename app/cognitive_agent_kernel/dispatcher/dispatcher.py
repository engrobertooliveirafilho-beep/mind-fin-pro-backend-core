class ExecutionDispatcher:
    def dispatch(self, plan):
        if plan["status"] == "PLANNED":
            return "EXECUTING_NOW"
        return "QUEUED"
