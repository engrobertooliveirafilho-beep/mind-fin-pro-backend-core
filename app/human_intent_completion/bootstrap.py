from app.human_intent_completion.reconstruction_engine.engine import IntentReconstructionEngine
from app.human_intent_completion.gap_filler.filler import SemanticGapFiller

class HICE:
    def __init__(self):
        self.reconstructor = IntentReconstructionEngine()
        self.filler = SemanticGapFiller()

    def process(self, user_input):
        intent = self.reconstructor.reconstruct(user_input)
        intent = self.filler.fill(intent)
        return intent
