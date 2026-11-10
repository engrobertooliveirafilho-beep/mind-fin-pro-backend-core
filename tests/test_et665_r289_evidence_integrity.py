"""ET665.R289 integrity gate regression tests; no strategy certification."""
import hashlib
from mind_trader.research.et665_r289_evidence_integrity import verify_evidence_files

def test_matching_bytes_still_quarantined(tmp_path):
    rule=tmp_path/"rule.py";ohlc=tmp_path/"candles.csv"
    rule.write_bytes(b"rule fixture")
    ohlc.write_bytes(b"ohlc fixture")
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    result=verify_evidence_files(rule,ohlc,sha(rule),sha(ohlc))
    assert result["integrity_verified"] is True
    assert result["causal_signal_verified"] is False
    assert result["runtime_promotion_allowed"] is False

def test_tampered_ohlc_fails_closed(tmp_path):
    rule=tmp_path/"rule.py";ohlc=tmp_path/"candles.csv"
    rule.write_bytes(b"rule");ohlc.write_bytes(b"original")
    rule_sha=hashlib.sha256(rule.read_bytes()).hexdigest()
    ohlc_sha=hashlib.sha256(ohlc.read_bytes()).hexdigest()
    ohlc.write_bytes(b"tampered")
    result=verify_evidence_files(rule,ohlc,rule_sha,ohlc_sha)
    assert result["ohlc_integrity"] is False
    assert result["integrity_verified"] is False

def test_missing_files_fail_closed(tmp_path):
    result=verify_evidence_files(tmp_path/"missing.py",tmp_path/"missing.csv","a"*64,"b"*64)
    assert result["integrity_verified"] is False

def test_invalid_declared_hash_fails_closed(tmp_path):
    rule=tmp_path/"rule.py";ohlc=tmp_path/"ohlc.csv"
    rule.write_bytes(b"x");ohlc.write_bytes(b"x")
    result=verify_evidence_files(rule,ohlc,"not-a-hash","0"*64)
    assert result["integrity_verified"] is False
