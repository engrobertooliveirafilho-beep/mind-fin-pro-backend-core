class PlanningEngine:
    def create_plan(self, goal):
        return {
            "steps": ["analyze", "decompose", "execute"],
            "status": "PLANNED"
        }

    def revise_plan(self, plan, feedback):
        plan["status"] = "REVISED"
        return plan
