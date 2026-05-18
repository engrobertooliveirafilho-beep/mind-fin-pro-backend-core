class PersonaFollowupResolver:
    SHORT_FOLLOWUPS = [
        "quais ajustes", "que ajustes", "quais mudanças", "que mudanças",
        "como assim", "por quê", "porque", "me explica", "detalha",
        "melhora o que", "ajustar o que", "quais exatamente"
    ]

    VISUAL_MEMORY_HINTS = [
        "rosto", "identidade visual", "persona", "neura", "imagem anterior",
        "confiável", "acolhedora", "premium", "humana", "futurista"
    ]

    def is_persona_followup(self, message: str, memory_context: str = "") -> bool:
        m = (message or "").lower().strip()
        ctx = (memory_context or "").lower()
        return any(k in m for k in self.SHORT_FOLLOWUPS) and any(h in ctx for h in self.VISUAL_MEMORY_HINTS)

    def expand(self, message: str, memory_context: str = "") -> str:
        m = (message or "").lower()
        if "ajuste" in m or "mudança" in m:
            return "quais ajustes práticos eu devo fazer no rosto/persona visual da Neura para ela parecer mais confiável, acolhedora e menos artificial?"
        return "continue a análise da identidade visual da Neura com base no contexto anterior, dando resposta direta, humana e estratégica."
