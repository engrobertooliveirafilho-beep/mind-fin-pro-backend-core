import csv, math
from pathlib import Path
from mind_trader.app.orchestration.paper_research_operation import run_paper_research_operation
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def write_csv(path):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_paper_research_operation_complete(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    write_csv(folder/"market.csv")
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=run_paper_research_operation(folder,"TEST","1m",str(tmp_path/"m.sqlite"),str(cfg),limit=3)
    assert r["decision"]=="PAPER_RESEARCH_OPERATION_COMPLETE"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_paper_research_operation_blocks_no_data(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=run_paper_research_operation(folder,"TEST","1m",str(tmp_path/"m.sqlite"),str(cfg),limit=3)
    assert r["decision"]=="BLOCKED_NO_VALID_DATA"
    assert r["production"]=="BLOCKED"
