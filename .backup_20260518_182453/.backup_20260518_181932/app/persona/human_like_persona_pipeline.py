from app.persona.visual_persona_response_layer import VisualPersonaResponseLayer
from app.persona.open_ended_reasoning_layer import OpenEndedReasoningLayer
from app.persona.emotional_dialogue_layer import EmotionalDialogueLayer
from app.persona.persona_continuity_memory import PersonaContinuityMemory
from app.persona.adaptive_social_dialogue import AdaptiveSocialDialogue
from app.persona.persona_followup_resolver import PersonaFollowupResolver

class HumanLikePersonaPipeline:
    def __init__(self):
        self.reasoning = OpenEndedReasoningLayer()
        self.visual = VisualPersonaResponseLayer()
        self.emotional = EmotionalDialogueLayer()
        self.memory = PersonaContinuityMemory()
        self.adaptive = AdaptiveSocialDialogue()
        self.followup = PersonaFollowupResolver()

    def can_handle(self, message: str, memory_context: str = "") -> bool:
        return self.reasoning.is_open_persona_question(message) or self.followup.is_persona_followup(message, memory_context)

    def answer(self, message: str, visual_context: str = "", memory_context: str = "", memory=None, sender_id: str = "") -> str:
        if self.followup.is_persona_followup(message, memory_context):
            message = self.followup.expand(message, memory_context)

        raw = self.visual.answer(message, visual_context, memory_context).text
        polished = self.emotional.polish(raw)
        adapted = self.adaptive.adapt(polished, message)

        if memory and sender_id:
            self.memory.persist(memory, sender_id, message)

        return adapted
