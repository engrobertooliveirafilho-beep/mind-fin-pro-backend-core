class ContextWeighting:
    def adjust(self, hypotheses, user_state):
        for h in hypotheses:
            if user_state.get("confused"):
                h["score"] += 0.2
        return hypotheses
