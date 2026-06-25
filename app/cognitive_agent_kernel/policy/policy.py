class ActionPolicy:
    def decide(self, goal, context):
        if "urgent" in goal.lower():
            return "EXECUTE_IMMEDIATELY"
        return "DEFER"
