import hashlib
import re

EMBEDDING_DIM = 256


def embed_text(text):
    """Offline lexical feature hashing, not semantic embeddings."""
    if not isinstance(text, str) or len(text) > 16384:
        raise ValueError('Invalid text')
    tokens = re.findall(r'\w+', text.casefold())
    if not tokens:
        raise ValueError('No lexical tokens')
    vector = [0.0] * EMBEDDING_DIM
    for token in tokens:
        index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], 'big') % EMBEDDING_DIM
        vector[index] += 1.0
    return vector
