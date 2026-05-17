class OpenEndedReasoningLayer:
    KEYWORDS = [
        "achou", "parece", "transmite", "alterar", "melhorar", "confiável",
        "humana", "futurista", "aceitarem", "resistência", "estilo", "combina",
        "opinião", "marca", "persona", "rosto"
    ]

    def is_open_persona_question(self, message: str) -> bool:
        m = (message or "").lower()
        return any(k in m for k in self.KEYWORDS)

    def classify(self, message: str) -> str:
        m = (message or "").lower()
        if "confi" in m or "alterar" in m or "melhorar" in m:
            return "improvement"
        if "humana" in m or "futurista" in m:
            return "comparison"
        if "aceit" in m or "resist" in m:
            return "adoption_strategy"
        if "estilo" in m or "combina" in m:
            return "brand_positioning"
        return "open_opinion"
