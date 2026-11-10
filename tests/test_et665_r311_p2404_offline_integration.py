import hashlib
import json
from mind_trader.research.et665_r311_p2404_offline_integration import analyze_verified_paper_csv

def sample(tmp_path,body="edge_id,timestamp,pnl_r\nA,1,1\nA,2,2\nA,3,3\nB,1,2\nB,2,4\nB,3,6\n"):
    source=tmp_path/"causal_candidate.csv"
    source.write_text(body,encoding="utf-8")
    manifest=tmp_path/"manifest.json"
    manifest.write_text(json.dumps({"schema":"ET665_TRUSTED_SOURCE_MANIFEST_V1",
      "sources":{"s1":{"source_kind":"CAUSAL_STRATEGY_REPLAY",
      "sha256":hashlib.sha256(source.read_bytes()).hexdigest()}}}),encoding="utf-8")
    return source,manifest,hashlib.sha256(manifest.read_bytes()).hexdigest()

def test_integrated_analysis_is_never_certified(tmp_path):
    src,man,anchor=sample(tmp_path)
    r=analyze_verified_paper_csv(src,man,anchor,source_id="s1")
    assert r["analysis_valid"] and len(r["pairs"])==1
    assert r["source_integrity_verified"] and not r["causal_signal_verified"]
    assert not r["runtime_promotion_allowed"] and not r["correlation_certified"]

def test_missing_anchor_rejected(tmp_path):
    src,man,_=sample(tmp_path)
    assert "TRUST_ANCHOR_REQUIRED" in analyze_verified_paper_csv(src,man,"",source_id="s1")["issues"]

def test_tampered_source_rejected(tmp_path):
    src,man,anchor=sample(tmp_path)
    src.write_text(src.read_text()+"A,4,2\n")
    assert "SOURCE_HASH_MISMATCH" in analyze_verified_paper_csv(src,man,anchor,source_id="s1")["issues"]

def test_historical_p2403e_quarantined(tmp_path):
    src,man,anchor=sample(tmp_path)
    old=src.rename(tmp_path/"p2403e_de40_edge_trade_series.csv")
    assert "HISTORICAL_SOURCE_QUARANTINED" in analyze_verified_paper_csv(old,man,anchor,source_id="s1")["issues"]

def test_duplicate_csv_header_rejected(tmp_path):
    src,man,anchor=sample(tmp_path,"edge_id,timestamp,pnl_r,pnl_r\nA,1,1,1\n")
    assert "INVALID_CSV_SCHEMA" in analyze_verified_paper_csv(src,man,anchor,source_id="s1")["issues"]

def test_malformed_row_rejected(tmp_path):
    src,man,anchor=sample(tmp_path,"edge_id,timestamp,pnl_r\nA,1,1,EXTRA\n")
    assert "MALFORMED_CSV" in analyze_verified_paper_csv(src,man,anchor,source_id="s1")["issues"]
