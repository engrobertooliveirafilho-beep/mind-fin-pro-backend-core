class PersonaContinuityMemory:
    def extract_preferences(self, message: str) -> dict:
        m = (message or "").lower()
        prefs = {}
        for key in ["humana", "futurista", "elegante", "jovem", "simpática", "premium", "cabelo", "expressão", "cor", "estilo"]:
            if key in m:
                prefs[key] = True
        return prefs

    def persist(self, memory, sender_id: str, message: str) -> bool:
        prefs = self.extract_preferences(message)
        if not prefs or memory is None:
            return False
        try:
            memory.save(sender_id, "PERSONA_VISUAL_PREFS::" + str(prefs))
            return True
        except Exception:
            return False
