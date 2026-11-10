import hashlib
import json
from mind_trader.research.et665_r305_pinned_authority_gate import verify_pinned_manifest

def fixture(tmp_path):
    source=tmp_path/"replay.csv"
    source.write_bytes(b"sample")
    manifest=tmp_path/"manifest.json"
    manifest.write_text(json.dumps({"schema":"ET665_TRUSTED_SOURCE_MANIFEST_V1",
        "sources":{"edge-a":{"source_kind":"CAUSAL_STRATEGY_REPLAY",
        "sha256":hashlib.sha256(b"sample").hexdigest()}}}))
    anchor=hashlib.sha256(manifest.read_bytes()).hexdigest()
    return source,manifest,anchor

def test_matching_pinned_manifest_integrity_only(tmp_path):
    source,manifest,anchor=fixture(tmp_path)
    r=verify_pinned_manifest(source,manifest,anchor,source_id="edge-a")
    assert r["authority_integrity_verified"] and r["source_integrity_verified"]
    assert not r["causal_signal_verified"] and not r["runtime_promotion_allowed"]

def test_manifest_tampering_rejected(tmp_path):
    source,manifest,anchor=fixture(tmp_path)
    manifest.write_bytes(manifest.read_bytes()+b" ")
    assert "MANIFEST_HASH_MISMATCH" in verify_pinned_manifest(source,manifest,anchor,source_id="edge-a")["issues"]

def test_source_tampering_rejected(tmp_path):
    source,manifest,anchor=fixture(tmp_path)
    source.write_bytes(b"changed")
    assert "SOURCE_HASH_MISMATCH" in verify_pinned_manifest(source,manifest,anchor,source_id="edge-a")["issues"]

def test_missing_external_anchor_rejected(tmp_path):
    source,manifest,_=fixture(tmp_path)
    assert "TRUST_ANCHOR_REQUIRED" in verify_pinned_manifest(source,manifest,"",source_id="edge-a")["issues"]

def test_unknown_source_rejected(tmp_path):
    source,manifest,anchor=fixture(tmp_path)
    assert "SOURCE_NOT_IN_MANIFEST" in verify_pinned_manifest(source,manifest,anchor,source_id="unknown")["issues"]

def test_symlink_manifest_rejected(tmp_path):
    source,manifest,anchor=fixture(tmp_path)
    link=tmp_path/"alias.json"
    link.symlink_to(manifest)
    assert "FILE_UNAVAILABLE_OR_SYMLINK" in verify_pinned_manifest(source,link,anchor,source_id="edge-a")["issues"]
