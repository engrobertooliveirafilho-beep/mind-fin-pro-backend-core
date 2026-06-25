class CognitiveCollisionRegistry:
    """
    P19P55: detect overlapping cognitive responsibilities.
    Shadow-only registry.
    """

    def __init__(self):
        self.registry = {}

    def register(self, module, capabilities):
        for c in capabilities:
            self.registry.setdefault(c, []).append(module)

    def get_collisions(self):
        return {k:v for k,v in self.registry.items() if len(v) > 1}
