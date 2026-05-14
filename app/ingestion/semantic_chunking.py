class SemanticChunker:
    def chunk(self, text: str, max_chars: int = 1200):
        text = text or ''
        return [{'index': i, 'content': text[i:i+max_chars], 'chars': len(text[i:i+max_chars])} for i in range(0, len(text), max_chars)]