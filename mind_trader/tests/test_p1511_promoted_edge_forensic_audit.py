import json
from app.p1511_promoted_edge_forensic_audit import engine

def test_p1511(tmp_path, monkeypatch):
    source=tmp_path/"promoted_edges.json"
    source.write_text(json.dumps([{"symbol":"TEST","timeframe":"M5","profit_factor":1.1,"trades":2,"walk_forward_approved":False,"monte_carlo_approved":False}]),encoding="utf-8")
    monkeypatch.setattr(engine,"INPUT",source)
    monkeypatch.chdir(tmp_path)
    r=engine.run()
    assert r["FORENSIC_APPROVED"]==0
    assert r["FORENSIC_REJECTED"]==1
    assert r["TOP_10_EDGES"]==[]
