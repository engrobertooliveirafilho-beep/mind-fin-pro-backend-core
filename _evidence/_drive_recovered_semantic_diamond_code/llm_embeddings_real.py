import os
import hashlib
from typing import List, Optional, Literal

ProviderName = Literal["openai", "mistral", "groq", "fake"]

DEFAULT_OPENAI_MODEL = os.environ.get("MIND_EMBEDDING_OPENAI_MODEL", "text-embedding-3-small")
DEFAULT_MISTRAL_MODEL = os.environ.get("MIND_EMBEDDING_MISTRAL_MODEL", "mistral-embed")
DEFAULT_GROQ_MODEL = os.environ.get("MIND_EMBEDDING_GROQ_MODEL", "text-embedding-3-small")

class EmbeddingClient:
    """
    Cliente de embeddings com múltiplos provedores.

    Provedores suportados:
# PATCHED_PLACEHOLDER OPENAI_API_KEY=__ENV_OPENAI_API_KEY__
    - "mistral": usa MISTRAL_API_KEY e DEFAULT_MISTRAL_MODEL
    - "groq": usa GROQ_API_KEY e DEFAULT_GROQ_MODEL
    - "fake": determinístico, offline, para testes

    Em testes, o backend "fake" é suficiente e não faz chamadas de rede.
    """

    def __init__(
        self,
        provider: ProviderName = "fake",
        model: Optional[str] = None,
        embedding_dim: int = 128,
    ) -> None:
        self.provider: ProviderName = provider
        self.embedding_dim = embedding_dim
# PATCHED_PLACEHOLDER OPENAI_API_KEY=__ENV_OPENAI_API_KEY__
        self.mistral_key = os.environ.get("MISTRAL_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")

        if provider == "openai":
            self.model = model or DEFAULT_OPENAI_MODEL
        elif provider == "mistral":
            self.model = model or DEFAULT_MISTRAL_MODEL
        elif provider == "groq":
            self.model = model or DEFAULT_GROQ_MODEL
        else:
            self.model = "fake-embedding-model"

    # --------------- API PÚBLICA ---------------

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Recebe lista de textos e retorna lista de embeddings.
        Sempre retorna algo, mesmo sem providers reais (fallback fake).
        """
        if not texts:
            return []

        if self.provider == "openai" and self.openai_key:
            try:
                import openai  # type: ignore[import-not-found]
                client = openai.OpenAI(api_key=self.openai_key)  # type: ignore[attr-defined]
                resp = client.embeddings.create(model=self.model, input=texts)
                return [d.embedding for d in resp.data]  # type: ignore[attr-defined]
            except Exception:
                # fallback silencioso para fake em caso de erro
                return [self._fake_embed(t) for t in texts]

        if self.provider == "mistral" and self.mistral_key:
            try:
                from mistralai import Mistral  # type: ignore[import-not-found]
                client = Mistral(api_key=self.mistral_key)
                resp = client.embeddings.create(model=self.model, input=texts)
                return [d.embedding for d in resp.data]  # type: ignore[attr-defined]
            except Exception:
                return [self._fake_embed(t) for t in texts]

        if self.provider == "groq" and self.groq_key:
            try:
                from groq import Groq  # type: ignore[import-not-found]
                client = Groq(api_key=self.groq_key)
                resp = client.embeddings.create(model=self.model, input=texts)
                return [d.embedding for d in resp.data]  # type: ignore[attr-defined]
            except Exception:
                return [self._fake_embed(t) for t in texts]

        # default + qualquer falha: fake determinístico
        return [self._fake_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """
        Versão simplificada para um único texto.
        """
        vectors = self.embed_texts([text])
        return vectors[0] if vectors else []

    # --------------- BACKEND FAKE ---------------

    def _fake_embed(self, text: str) -> List[float]:
        """
        Embedding determinístico, offline, sem dependências externas.
        Usa SHA256 para gerar embedding_dim floats em [-1, 1].
        """
        if not text:
            text = "<EMPTY>"

        h = hashlib.sha256(text.encode("utf-8")).digest()
        # repete o hash até cobrir embedding_dim
        needed = self.embedding_dim
        data = (h * ((needed // len(h)) + 1))[:needed]
        # mapeia byte [0,255] -> float [-1, 1]
        return [((b / 255.0) * 2.0) - 1.0 for b in data]
