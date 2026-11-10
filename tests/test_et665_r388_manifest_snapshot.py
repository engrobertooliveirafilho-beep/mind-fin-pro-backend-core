"""ET665.R389: adversarial immutable-manifest regression, offline only."""
import hashlib
import json
from pathlib import Path
from mind_trader.research import et665_r311_p2404_offline_integration as pipeline


def _fixture(tmp_path):
    source = tmp_path / "candidate.csv"
    source.write_text("edge_id,timestamp,pnl_r\nA,1,1\nA,2,2\nA,3,3\nB,1,2\nB,2,4\nB,3,6\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "schema": "ET665_TRUSTED_SOURCE_MANIFEST_V1",
        "sources": {"s1": {
            "source_kind": "CAUSAL_STRATEGY_REPLAY",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "generator": "independent_replay_v1",
            "lineage": "fixture_only",
            "independent_review": True,
        }},
    }), encoding="utf-8")
    return source, manifest, hashlib.sha256(manifest.read_bytes()).hexdigest()


def test_pinned_metadata_survives_manifest_swap(tmp_path, monkeypatch):
    source, manifest, anchor = _fixture(tmp_path)
    original_gate = pipeline.verify_pinned_manifest

    def swap_after_gate(*args, **kwargs):
        verified = original_gate(*args, **kwargs)
        assert verified["source_integrity_verified"]
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        doc["sources"]["s1"]["generator"] = "p2403e_noncausal_generator"
        doc["sources"]["s1"]["independent_review"] = False
        manifest.write_text(json.dumps(doc), encoding="utf-8")
        return verified

    monkeypatch.setattr(pipeline, "verify_pinned_manifest", swap_after_gate)
    result = pipeline.analyze_verified_paper_csv(source, manifest, anchor, source_id="s1")
    assert result["analysis_valid"] and len(result["pairs"]) == 1
    assert result["authority_integrity_verified"]
    assert result["source_integrity_verified"]
    assert not result["causal_signal_verified"]
    assert not result["correlation_certified"]
    assert not result["runtime_promotion_allowed"]


def test_tampered_manifest_before_gate_rejected(tmp_path):
    source, manifest, anchor = _fixture(tmp_path)
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    doc["sources"]["s1"]["independent_review"] = False
    manifest.write_text(json.dumps(doc), encoding="utf-8")
    result = pipeline.analyze_verified_paper_csv(source, manifest, anchor, source_id="s1")
    assert "MANIFEST_HASH_MISMATCH" in result["issues"]
    assert not result["analysis_valid"]
    assert not result["runtime_promotion_allowed"]
