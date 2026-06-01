import os
import hashlib
from typing import List
import json

import httpx

EMBEDDINGS_MODE = os.getenv('EMBEDDINGS_MODE', 'fake')  # 'fake' | 'real'
EMBEDDINGS_PROVIDER = os.getenv('EMBEDDINGS_PROVIDER', 'openai')  # 'openai' | future: 'mistral', 'groq'

EMBEDDING_DIM = 256


def _fake_embedding(text: str) -> List[float]:
    h = hashlib.sha256(text.encode('utf-8')).digest()
    floats = []
    for i in range(EMBEDDING_DIM):
        b = h[i % len(h)]
        v = (b - 128) / 128.0
        floats.append(float(v))
    return floats


async def _embed_openai(text: str) -> List[float]:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # fallback seguro: não quebra se não tiver chave
        return _fake_embedding(text)

    url = 'https://api.openai.com/v1/embeddings'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': os.getenv('OPENAI_EMBEDDINGS_MODEL', 'text-embedding-3-small'),
        'input': text,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return [float(x) for x in data['data'][0]['embedding']]


def embed_text(text: str) -> List[float]:
    if not text:
        return _fake_embedding('')

    if EMBEDDINGS_MODE != 'real':
        return _fake_embedding(text)

    # modo real ativado
    if EMBEDDINGS_PROVIDER == 'openai':
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return loop.run_until_complete(_embed_openai(text))
            return asyncio.run(_embed_openai(text))
        except Exception:
            # fallback seguro em qualquer erro de rede/API
            return _fake_embedding(text)

    # provider desconhecido -> fallback
    return _fake_embedding(text)
