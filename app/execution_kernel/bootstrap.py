from app.execution_kernel.event_core.event_bus import EventBus
from app.execution_kernel.state.store import GlobalStateStore
from app.execution_kernel.intent.engine import IntentEngine
from app.execution_kernel.execution.engine import ExecutionEngine
from app.execution_kernel.feedback.loop import FeedbackLoop

class CognitiveExecutionKernel:
    def __init__(self):
        self.bus = EventBus()
        self.state = GlobalStateStore()
        self.intent = IntentEngine()
        self.executor = ExecutionEngine()
        self.feedback = FeedbackLoop()

    def run(self, input_data):
        event = self.bus.emit(input_data)

        intent = self.intent.parse(event)
        result = self.executor.execute(intent)
        evaluation = self.feedback.evaluate(result)

        self.state.update("last_result", result)

        return {
            "intent": intent,
            "result": result,
            "evaluation": evaluation
        }
