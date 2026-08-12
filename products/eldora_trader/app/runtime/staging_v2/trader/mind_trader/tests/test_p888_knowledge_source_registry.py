from mind_trader.app.knowledge.knowledge_source_registry import register_knowledge_source, require_source_registered, source_hash

def test_source_hash_len():
    assert len(source_hash("abc"))==64

def test_register_knowledge_source(tmp_path):
    p=tmp_path/"sources.json"
    r=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(p))
    assert r["status"]=="REGISTERED_FOR_RESEARCH"
    assert r["production"]=="BLOCKED"

def test_blocks_bad_source_type(tmp_path):
    r=register_knowledge_source("x","BAD","text",str(tmp_path/"s.json"))
    assert r["decision"]=="BLOCK_SOURCE_TYPE"

def test_require_source_registered_ok(tmp_path):
    p=tmp_path/"sources.json"
    s=register_knowledge_source("note","MANUAL_RESEARCH","liquidity sweep",str(p))
    r=require_source_registered(s["source_id"],str(p))
    assert r["allowed"] is True
    assert r["decision"]=="SOURCE_OK"

def test_require_source_missing_blocks(tmp_path):
    r=require_source_registered("missing",str(tmp_path/"sources.json"))
    assert r["allowed"] is False
