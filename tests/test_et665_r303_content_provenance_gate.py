import hashlib
from pathlib import Path
from mind_trader.research.et665_r303_content_provenance_gate import verify_source_bytes

def test_renaming_cannot_bypass_hash_gate(tmp_path):
    source=tmp_path/"p2403b_edge_trade_series.csv"
    source.write_bytes(b"untrusted")
    digest=hashlib.sha256(b"trusted").hexdigest()
    source.rename(tmp_path/"renamed.csv")
    r=verify_source_bytes(tmp_path/"renamed.csv",digest,authority_verified=True)
    assert "SHA256_MISMATCH" in r["issues"]
    assert not r["runtime_promotion_allowed"]

def test_matching_digest_without_authority_rejected(tmp_path):
    source=tmp_path/"data.csv"
    source.write_bytes(b"known")
    digest=hashlib.sha256(b"known").hexdigest()
    assert "TRUSTED_AUTHORITY_REQUIRED" in verify_source_bytes(source,digest)["issues"]

def test_matching_digest_does_not_certify_causality(tmp_path):
    source=tmp_path/"data.csv"
    source.write_bytes(b"known")
    digest=hashlib.sha256(b"known").hexdigest()
    r=verify_source_bytes(source,digest,authority_verified=True)
    assert r["integrity_verified"]
    assert not r["causal_signal_verified"] and not r["runtime_promotion_allowed"]

def test_modified_bytes_rejected(tmp_path):
    source=tmp_path/"data.csv"
    source.write_bytes(b"old")
    digest=hashlib.sha256(b"old").hexdigest()
    source.write_bytes(b"new")
    assert "SHA256_MISMATCH" in verify_source_bytes(source,digest,authority_verified=True)["issues"]

def test_invalid_digest_rejected(tmp_path):
    source=tmp_path/"data.csv"
    source.write_bytes(b"known")
    assert "TRUSTED_SHA256_REQUIRED" in verify_source_bytes(source,"bad",authority_verified=True)["issues"]

def test_missing_file_rejected(tmp_path):
    assert "SOURCE_NOT_REGULAR_FILE" in verify_source_bytes(tmp_path/"missing.csv","0"*64,authority_verified=True)["issues"]

def test_symlink_rejected(tmp_path):
    source=tmp_path/"data.csv"
    source.write_bytes(b"known")
    link=tmp_path/"link.csv"
    link.symlink_to(source)
    digest=hashlib.sha256(b"known").hexdigest()
    assert "SOURCE_NOT_REGULAR_FILE" in verify_source_bytes(link,digest,authority_verified=True)["issues"]
