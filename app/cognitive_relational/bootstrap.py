from app.cognitive_relational.user_model.profile import *
from app.cognitive_relational.question_engine.engine import *

class RelationalCognitiveCore:
    def __init__(self):
        self.mode = "RELATIONAL_ACTIVE"

    def interact(self, input):
        return {
            "response_mode": "multi_message_enabled",
            "questions": True,
            "profiling": True
        }
