import os

class EmbeddingProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("NEURA_EMBEDDING_MODEL", "text-embedding-3-small")

    def embed(self, text: str):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        if not text or not text.strip():
            return None
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        emb = client.embeddings.create(model=self.model, input=text[:8000]).data[0].embedding
        if not emb or len(emb) != 1536:
            raise RuntimeError(f"invalid_embedding_dimension:{len(emb) if emb else 0}")
        return emb
