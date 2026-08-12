from pathlib import Path

p = Path("app/embedding/provider.py")
s = p.read_text(encoding="utf-8")

new = '''import os

class EmbeddingProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("NEURA_EMBEDDING_MODEL", "text-embedding-3-small")
        self.last_error = None

    def embed(self, text: str):
        self.last_error = None

        if not self.api_key:
            self.last_error = "OPENAI_API_KEY not configured"
            return None

        if not text or not text.strip():
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            emb = client.embeddings.create(model=self.model, input=text[:8000]).data[0].embedding

            if not emb or len(emb) != 1536:
                self.last_error = f"invalid_embedding_dimension:{len(emb) if emb else 0}"
                return None

            return emb

        except Exception as e:
            self.last_error = f"{type(e).__name__}: {str(e)[:500]}"
            return None
'''

p.write_text(new, encoding="utf-8")
print("PATCH_EMBEDDING_PROVIDER_OK")
