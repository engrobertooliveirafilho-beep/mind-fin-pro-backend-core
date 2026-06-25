class PersonalityStabilityGuard:
    def enforce(self, personality):
        for k, v in personality["adaptive_traits"].items():
            personality["adaptive_traits"][k] = max(0, min(1, v))
        return personality
