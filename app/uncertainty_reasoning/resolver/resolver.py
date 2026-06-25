class IntentResolver:
    def resolve(self, hypotheses):
        return hypotheses[0]  # top probability winner
