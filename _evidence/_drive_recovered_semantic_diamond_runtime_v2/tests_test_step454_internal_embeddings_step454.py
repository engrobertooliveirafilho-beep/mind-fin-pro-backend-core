from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_step454_internal_embeddings_basic():
    payload = {
        "text": "MIND FIN PRO embeddings internos",
        "namespace": "mind_test",
        "dim": 32
    }
    r = client.post('/ai/embeddings/internal/embed', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["namespace"] == "mind_test"
    assert data["dim"] == 32
    vec = data["vector"]
    assert isinstance(vec, list)
    assert len(vec) == 32
    # valores entre 0 e 1
    for v in vec:
        assert 0.0 <= v <= 1.0
    # chamada repetida deve gerar mesmo checksum
    r2 = client.post('/ai/embeddings/internal/embed', json=payload)
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["checksum"] == data["checksum"]
