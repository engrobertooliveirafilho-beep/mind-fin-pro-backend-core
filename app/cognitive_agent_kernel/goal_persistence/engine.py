class GoalPersistenceEngine:
    def __init__(self):
        self.goals = {}

    def add_goal(self, goal_id, goal):
        self.goals[goal_id] = {
            "goal": goal,
            "status": "ACTIVE"
        }

    def get_active_goals(self):
        return [g for g in self.goals.values() if g["status"] == "ACTIVE"]
