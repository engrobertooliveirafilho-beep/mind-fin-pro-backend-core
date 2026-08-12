class PolicyEngine:
    def decide(self, reasoning):
        return max(reasoning['hypotheses'])
