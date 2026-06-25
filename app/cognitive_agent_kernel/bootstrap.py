from app.cognitive_agent_kernel.goal_persistence.engine import GoalPersistenceEngine
from app.cognitive_agent_kernel.planner.planner import PlanningEngine
from app.cognitive_agent_kernel.dispatcher.dispatcher import ExecutionDispatcher
from app.cognitive_agent_kernel.world_model.model import WorldModel
from app.cognitive_agent_kernel.policy.policy import ActionPolicy

class CognitiveAgentKernel:
    def __init__(self):
        self.goals = GoalPersistenceEngine()
        self.planner = PlanningEngine()
        self.dispatcher = ExecutionDispatcher()
        self.world = WorldModel()
        self.policy = ActionPolicy()

    def step(self, input_event):
        self.world.update(input_event)

        plan = self.planner.create_plan(input_event)
        decision = self.policy.decide(input_event, self.world.state)

        return {
            "plan": plan,
            "decision": decision
        }
