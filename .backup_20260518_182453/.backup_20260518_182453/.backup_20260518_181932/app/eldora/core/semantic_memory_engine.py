import math
import hashlib

VECTOR_MEMORY = []
SEMANTIC_GRAPH = {}

def fake_embedding(text: str, dims: int = 16):
    h = hashlib.sha256(text.encode()).digest()
    return [((h[i] / 255.0) * 2 - 1) for i in range(dims)]

def cosine_similarity(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def store_memory(text: str, metadata: dict | None = None):
    embedding = fake_embedding(text)

    item = {
        "text": text,
        "embedding": embedding,
        "metadata": metadata or {}
    }

    VECTOR_MEMORY.append(item)

    node = metadata.get("node", "default") if metadata else "default"
    SEMANTIC_GRAPH.setdefault(node, []).append(text)

    return {
        "status": "ok",
        "stored": True,
        "memory_size": len(VECTOR_MEMORY)
    }

def retrieve_memory(query: str, top_k: int = 3):
    q = fake_embedding(query)

    scored = []

    for item in VECTOR_MEMORY:
        score = cosine_similarity(q, item["embedding"])
        scored.append({
            "score": score,
            "text": item["text"],
            "metadata": item["metadata"]
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "status": "ok",
        "query": query,
        "results": scored[:top_k]
    }

def semantic_graph_report():
    return {
        "status": "ok",
        "nodes_total": len(SEMANTIC_GRAPH),
        "graph": SEMANTIC_GRAPH
    }
