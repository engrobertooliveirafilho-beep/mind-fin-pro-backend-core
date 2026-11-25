import json
from pathlib import Path
import pytest
from app.p9_dna_extraction_engine.engine import extract_dna, dna_to_genome_candidates, run, source_id


def test_p94_run_without_source_fails_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest = run()
    assert manifest["STATUS"] == "P9.4_BLOCKED_SOURCE_REQUIRED"
    assert manifest["DNA_CANDIDATES"] == 0
    assert manifest["EXPORT_READY"] is False
    assert json.loads(Path("reports/P9.4_DNA_EXTRACTION_ENGINE/P9.4_dna_candidates.json").read_text())["dna_candidates"] == []


def test_p94_hash_covers_full_source_not_only_prefix():
    prefix = "trend " * 100
    assert source_id(prefix + "risk", "note") != source_id(prefix + "macro", "note")


def test_p94_extracts_candidates_from_explicit_source_with_provenance():
    source = extract_dna("Trend, volatility and liquidity are discussed.", "paper", "Source A")
    assert source["source_sha256"] == source_id("Trend, volatility and liquidity are discussed.", "paper")
    assert {x["tag"] for x in source["dna_candidates"]} == {"trend", "volatility", "liquidity"}
    assert all(x["source_sha256"] == source["source_sha256"] for x in source["dna_candidates"])


def test_p94_same_prefix_different_content_produces_distinct_ids():
    a = extract_dna("trend " * 100 + "risk", "note", "Same")
    b = extract_dna("trend " * 100 + "macro", "note", "Same")
    assert a["source_id"] != b["source_id"]
    assert a["dna_candidates"][0]["dna_id"] != b["dna_candidates"][0]["dna_id"]


def test_p94_rejects_empty_source_and_invalid_type():
    with pytest.raises(ValueError, match="REAL_KNOWLEDGE_SOURCE_REQUIRED"):
        extract_dna("   ", "note", "x")
    with pytest.raises(ValueError, match="UNSUPPORTED_SOURCE_TYPE"):
        extract_dna("trend", "unknown", "x")


def test_p94_genome_candidates_require_matching_provenance():
    dna = extract_dna("breakout risk", "note", "x")
    candidates = dna_to_genome_candidates(dna)
    assert candidates
    assert all(x["source_sha256"] == dna["source_sha256"] for x in candidates)
    assert all(x["live_allowed"] is False and x["promotion_allowed"] is False for x in candidates)
    dna["dna_candidates"][0]["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="DNA_SOURCE_PROVENANCE_MISMATCH"):
        dna_to_genome_candidates(dna)


def test_p94_run_with_explicit_source_never_certifies_edge(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest = run("trend volatility", "paper", "Paper X")
    assert manifest["STATUS"] == "P9.4_CANDIDATES_EXTRACTED_UNVALIDATED"
    assert manifest["SOURCE_PROVENANCE"] == "SHA256_RECORDED"
    assert manifest["EDGE"] == "NOT_PROVEN"
    assert manifest["PROMOTION_ALLOWED"] is False
    assert manifest["EXPORT_READY"] is False


def test_p94_keyword_tagger_does_not_claim_semantic_understanding():
    dna = extract_dna("trend", "note", "x")
    assert dna["extraction_method"] == "BOUNDED_KEYWORD_TAGGING"
    assert "semantic validation required" in dna["dna_candidates"][0]["hypothesis"]
