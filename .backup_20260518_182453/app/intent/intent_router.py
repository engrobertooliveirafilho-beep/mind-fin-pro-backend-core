class IntentRouter:

    def detect(self, text:str):

        t=(text or "").lower()

        if any(x in t for x in ["estudar","prova","matemática","resumo"]):
            return "TutorAgent"

        if any(x in t for x in ["planejar","agenda","meta"]):
            return "PlannerAgent"

        if any(x in t for x in ["codigo","python","api"]):
            return "CodeAgent"

        if any(x in t for x in ["imagem","foto","vision"]):
            return "VisionAgent"

        if any(x in t for x in ["audio","voz","fala"]):
            return "VoiceAgent"

        return "MasterOrchestratorAgent"
