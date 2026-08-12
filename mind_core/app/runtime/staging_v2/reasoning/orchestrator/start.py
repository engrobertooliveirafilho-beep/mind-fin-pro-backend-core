from orchestrator.core.router import ExecutionRouter

router = ExecutionRouter()

def run(task):
    return router.route(task)
