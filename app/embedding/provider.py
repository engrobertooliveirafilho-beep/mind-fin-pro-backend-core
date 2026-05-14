import os

class EmbeddingProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("NEURA_EMBEDDING_MODEL", "text-embedding-3-small")

    def embed(self, text: str):
        if not text or not text.strip():
            return None
        text = text[:8000]
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            return client.embeddings.create(model=self.model, input=text).data[0].embedding
        except Exception:
            import openai
            if self.api_key:
                openai.api_key = self.api_key
            resp = openai.Embedding.create(model=self.model, input=text)
            return resp["data"][0]["embedding"]
