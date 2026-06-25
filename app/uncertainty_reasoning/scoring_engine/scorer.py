class ProbabilityScorer:
    def score(self, hypotheses, context):
        for h in hypotheses:
            h["score"] = h["confidence"] * 0.8
        return sorted(hypotheses, key=lambda x: x["score"], reverse=True)
