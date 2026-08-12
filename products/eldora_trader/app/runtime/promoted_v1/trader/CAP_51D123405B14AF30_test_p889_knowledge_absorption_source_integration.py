from pathlib import Path
from mind_trader.app.knowledge.knowledge_absorption_authority import absorb_knowledge_texts
from mind_trader.app.knowledge.knowledge_source_registry import register_knowledge_source

def test_absorption_blocks_without_source():
    r=absorb_knowledge_texts(["liquidity sweep"],"batch")
    assert r["decision"]=="BLOCK_ABSORPTION_SOURCE_REQUIRED"

def test_absorption_blocks_unregistered_source(tmp_path):
    r=absorb_knowledge_texts(["liquidity sweep"],"batch","missing",str(tmp_path/"sources.json"))
    assert r["decision"]=="BLOCK_ABSORPTION_SOURCE_NOT_REGISTERED"

def test_absorption_with_registered_source(tmp_path):
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(registry))
    r=absorb_knowledge_texts(["liquidity sweep"],"batch",src["source_id"],str(registry))
    assert r["decision"]=="KNOWLEDGE_ABSORBED_AS_REGISTERED_CANDIDATES"
    assert r["atoms_created"]==1
    assert r["atoms"][0]["registered_source_id"]==src["source_id"]
    assert r["production"]=="BLOCKED"

def test_registered_absorption_report_written(tmp_path):
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(registry))
    absorb_knowledge_texts(["liquidity sweep"],"batch",src["source_id"],str(registry))
    assert Path("mind_trader/reports/P8.89_knowledge_absorption_registered.json").exists()
