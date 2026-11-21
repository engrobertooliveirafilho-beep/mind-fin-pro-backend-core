"""Offline in-memory vector index. No persistence, network, or trade execution."""
import math

class IndexErrorSafety(ValueError):
    pass

class VectorIndex:
    def __init__(self, dimension, namespace='default'):
        if isinstance(dimension, bool) or not isinstance(dimension, int) or not 8 <= dimension <= 4096:
            raise IndexErrorSafety('dimension out of range')
        if not isinstance(namespace, str) or not namespace.strip():
            raise IndexErrorSafety('namespace required')
        self.dimension = dimension
        self.namespace = namespace
        self._vectors = {}

    def _validate(self, vector):
        if not isinstance(vector, (list, tuple)) or len(vector) != self.dimension:
            raise IndexErrorSafety('dimension mismatch')
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
            raise IndexErrorSafety('nonfinite vector')
        norm = math.sqrt(math.fsum(v * v for v in vector))
        if not math.isfinite(norm) or norm == 0:
            raise IndexErrorSafety('invalid norm')
        return tuple(v / norm for v in vector)

    def add(self, source_id, vector):
        if not isinstance(source_id, str) or not source_id.strip():
            raise IndexErrorSafety('source_id required')
        if source_id in self._vectors:
            raise IndexErrorSafety('duplicate source_id')
        normalized = self._validate(vector)
        self._vectors[source_id] = normalized

    def search(self, vector, limit=5):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise IndexErrorSafety('invalid limit')
        query = self._validate(vector)
        matches = [{'source_id': key, 'score': math.fsum(a*b for a,b in zip(query, val)), 'namespace': self.namespace} for key,val in self._vectors.items()]
        return sorted(matches, key=lambda x: (-x['score'], x['source_id']))[:limit]
