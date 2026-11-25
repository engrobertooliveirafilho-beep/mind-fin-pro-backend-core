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


def test_unregistered_content_hash_blocks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(registry))
    r=absorb_knowledge_texts(["breakout"],"batch",src["source_id"],str(registry))
    assert r["decision"]=="BLOCK_ABSORPTION_CONTENT_HASH_MISMATCH"
    assert r["production"]=="BLOCKED"
    assert not Path("mind_trader/reports/P8.89_knowledge_absorption_registered.json").exists()


def test_invalid_absorption_batches_block(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry=tmp_path/"sources.json"
    src=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(registry))
    for batch in (None, [], "liquidity sweep", [None], [""], [42]):
        r=absorb_knowledge_texts(batch,"batch",src["source_id"],str(registry))
        assert r["decision"]=="BLOCK_INVALID_ABSORPTION_TEXTS"
        assert r["production"]=="BLOCKED"
    assert not Path("mind_trader/reports/P8.89_knowledge_absorption_registered.json").exists()
