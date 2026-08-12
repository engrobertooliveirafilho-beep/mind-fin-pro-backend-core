from pathlib import Path
from mind_trader.app.knowledge.knowledge_absorption_authority import classify_text, extract_candidate_atom, absorb_knowledge_texts
from mind_trader.app.knowledge.knowledge_source_registry import register_knowledge_source

def test_classify_text_liquidity():
    assert classify_text("liquidity sweep after stop hunt")=="liquidity"

def test_extract_candidate_atom_no_edge():
    a=extract_candidate_atom("breakout above range with volume expansion","src")
    assert a["knowledge_status"]=="CANDIDATE_NOT_VALIDATED"
    assert a["edge_claim"]=="NONE"
    assert a["valid"] is True

def test_absorb_knowledge_texts(tmp_path):
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("batch","MANUAL_RESEARCH","pullback retest after trend volume absorption",str(registry))
    r=absorb_knowledge_texts(["pullback retest after trend","volume absorption"],"batch",src["source_id"],str(registry))
    assert r["decision"]=="KNOWLEDGE_ABSORBED_AS_REGISTERED_CANDIDATES"
    assert r["atoms_created"]==2
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_knowledge_report_written(tmp_path):
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("batch","MANUAL_RESEARCH","liquidity sweep",str(registry))
    absorb_knowledge_texts(["liquidity sweep"],"batch",src["source_id"],str(registry))
    assert Path("mind_trader/reports/P8.89_knowledge_absorption_registered.json").exists()
