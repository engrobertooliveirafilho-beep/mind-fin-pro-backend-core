class ReEvaluationLoop:
    def update(self, new_input, current_state):
        return {
            "recomputed": True,
            "state": current_state
        }
