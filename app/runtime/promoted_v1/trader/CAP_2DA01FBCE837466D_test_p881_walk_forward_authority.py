from pathlib import Path
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority, save_walk_forward_authority

def test_walk_forward_insufficient_windows():
    r=walk_forward_authority([{"expectancy":1}])
    assert r["passed"] is False
    assert r["decision"]=="WALK_FORWARD_INSUFFICIENT_WINDOWS"

def test_walk_forward_pass_research_only():
    r=walk_forward_authority([
        {"expectancy":1,"profit_factor":1.3},
        {"expectancy":0.5,"profit_factor":1.2},
        {"expectancy":0.2,"profit_factor":1.1}
    ])
    assert r["passed"] is True
    assert r["decision"]=="WALK_FORWARD_PASS_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_walk_forward_rejects_instability():
    r=walk_forward_authority([
        {"expectancy":1,"profit_factor":1.3},
        {"expectancy":-2,"profit_factor":0.7},
        {"expectancy":1,"profit_factor":1.2}
    ])
    assert r["passed"] is False

def test_save_walk_forward_authority(tmp_path):
    p=save_walk_forward_authority({"ok":True},str(tmp_path/"wf.json"))
    assert Path(p).exists()
