import json

class CapabilityGate:
    def __init__(self):
        self.registry = {
            "vision": False,
            "video": False,
            "text": True
        }

    def validate(self, modality):
        return self.registry.get(modality, False)
