import os
from openai import OpenAI
class EmbeddingProvider:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("NEURA_EMBEDDING_MODEL","text-embedding-3-small")
    def embed(self,text:str):
        if not text or not text.strip(): return None
        return self.client.embeddings.create(model=self.model,input=text[:8000]).data[0].embedding
