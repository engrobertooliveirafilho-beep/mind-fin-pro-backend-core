from app.capability_router.detector.detector import ModalityDetector
from app.capability_router.router.router import CapabilityRouter

class MCR:
    def __init__(self):
        self.detector = ModalityDetector()
        self.router = CapabilityRouter()

    def process(self, input_text):
        modality = self.detector.detect(input_text)
        return self.router.route(modality)
