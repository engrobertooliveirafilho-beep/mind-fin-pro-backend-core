class EducationalPromptBuilder:
    def build(self, user_message: str, memory_context: str = '') -> str:
        return f'VocÃª Ã© a NEURA, tutora cognitiva. Explique com definiÃ§Ã£o, exemplo, aplicaÃ§Ã£o e pergunta de checagem. Contexto: {memory_context}. Pergunta: {user_message}'