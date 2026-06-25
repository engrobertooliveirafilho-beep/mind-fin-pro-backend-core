from app.capability_router.gate.gate import CapabilityGate

class CapabilityRouter:
    def __init__(self):
        self.gate = CapabilityGate()

    def route(self, modality):
        if not self.gate.validate(modality):
            return {
                "status": "UNSUPPORTED_CAPABILITY",
                "fallback": "explicit_decline"
            }

        return {
            "status": "SUPPORTED",
            "execution": "proceed"
        }
