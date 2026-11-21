"""Deterministic lexical hashing vectors, not neural semantic embeddings."""
import hashlib
import math
import re

class EmbeddingError(ValueError):
    pass

def embed(text, *, namespace='default', dim=32):
    if not isinstance(text, str) or not text.strip():
        raise EmbeddingError('nonempty text required')
    if not isinstance(namespace, str) or not namespace.strip():
        raise EmbeddingError('namespace required')
    if isinstance(dim, bool) or not isinstance(dim, int) or not 8 <= dim <= 256:
        raise EmbeddingError('dim must be 8..256')
    tokens = re.findall(r'\w+', text.casefold(), flags=re.UNICODE)
    vec = [0.0] * dim
    for token in tokens:
        digest = hashlib.sha256((namespace + '\0' + token).encode('utf-8')).digest()
        slot = int.from_bytes(digest[:8], 'big') % dim
        sign = 1.0 if digest[8] & 1 else -1.0
        vec[slot] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm:
        vec = [v / norm for v in vec]
    return {'namespace': namespace, 'dim': dim, 'vector': vec,
            'checksum': hashlib.sha256((namespace + '\0' + text).encode('utf-8')).hexdigest(),
            'method': 'lexical_hashing_v1', 'semantic_model': False}
