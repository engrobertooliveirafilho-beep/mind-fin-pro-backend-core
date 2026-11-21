import json
import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import RuntimePersistence

def test_atomic_snapshot_round_trip(tmp_path):
    path = tmp_path / "runtime_state.json"
    store = RuntimePersistence(str(path))
    store.save({"equity": 100.0, "positions": [{"id": "PAPER_1"}]})
    assert store.load()["positions"][0]["id"] == "PAPER_1"
    assert not list(tmp_path.glob("*.tmp"))

def test_failed_serialization_preserves_prior_snapshot(tmp_path):
    path = tmp_path / "runtime_state.json"
    store = RuntimePersistence(str(path))
    store.save({"version": 1})
    before = path.read_bytes()
    with pytest.raises(ValueError):
        store.save({"equity": float("nan")})
    assert path.read_bytes() == before
    assert store.load() == {"version": 1}

def test_invalid_snapshot_shape_rejected(tmp_path):
    path = tmp_path / "runtime_state.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="INVALID_PAPER_RUNTIME_SNAPSHOT"):
        RuntimePersistence(str(path)).load()

def test_missing_snapshot_does_not_claim_recovery(tmp_path):
    store = RuntimePersistence(str(tmp_path / "missing.json"))
    assert store.load() == {}

def test_corrupt_snapshot_fails_closed(tmp_path):
    path = tmp_path / "runtime_state.json"
    path.write_text('{"equity":', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        RuntimePersistence(str(path)).load()
