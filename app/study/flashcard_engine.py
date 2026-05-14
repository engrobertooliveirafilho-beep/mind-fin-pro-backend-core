class FlashcardEngine:
    def generate(self, topic: str):
        return [{'front': f'O que Ã© {topic}?', 'back': f'Defina {topic} e dÃª um exemplo.'}]