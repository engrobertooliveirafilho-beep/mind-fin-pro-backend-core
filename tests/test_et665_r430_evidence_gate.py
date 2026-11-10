"""ET665.R430: evidence gate adversarial tests; no broker, no network."""
import hashlib
import json
import pytest
from mind_trader.research.et665_r391_evidence_gate import evaluate, FRONTS, AGENTS


def _fixture(tmp_path):
    component = tmp_path / "component.py"
    component.write_text("def run(): return 1\n", encoding="utf-8")
    digest = hashlib.sha256(component.read_bytes()).hexdigest()
    proof = tmp_path / "proof.json"
    proof.write_text('{"result":"PASS"}', encoding="utf-8")
    proof_sha = hashlib.sha256(proof.read_bytes()).hexdigest()
    entry = {"path": "proof.json", "sha256": proof_sha, "result": "PASS"}
    manifest = tmp_path / "manifest.json"
    doc = {"schema": "ET665_R391_EVIDENCE_V1",
           "component": {"path": "component.py", "sha256": digest},
           "fronts": {name: dict(entry) for name in FRONTS},
           "agents": {name: dict(entry) for name in AGENTS}}
    manifest.write_text(json.dumps(doc), encoding="utf-8")
    return manifest, doc, proof


def test_same_forged_pass_file_cannot_certify(tmp_path):
    manifest, _, _ = _fixture(tmp_path)
    result = evaluate(tmp_path, manifest)
    assert not result["certified"]
    assert result["evidence_complete"]
    assert result["agents_pass"] == 19 and result["fronts_pass"] == 16


def test_tampered_evidence_rejected(tmp_path):
    manifest, _, proof = _fixture(tmp_path)
    proof.write_text('{"result":"FAIL"}', encoding="utf-8")
    result = evaluate(tmp_path, manifest)
    assert result["agents_pass"] == 0 and result["fronts_pass"] == 0
    assert not result["evidence_complete"] and not result["certified"]


def test_missing_agent_rejected(tmp_path):
    manifest, doc, _ = _fixture(tmp_path)
    del doc["agents"]["HP19_19"]
    manifest.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValueError, match="COVERAGE_INCOMPLETE"):
        evaluate(tmp_path, manifest)


def test_tampered_component_rejected(tmp_path):
    manifest, _, _ = _fixture(tmp_path)
    (tmp_path / "component.py").write_text("def run(): return 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="COMPONENT_HASH_MISMATCH"):
        evaluate(tmp_path, manifest)
