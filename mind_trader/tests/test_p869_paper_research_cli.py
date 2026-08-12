import csv, math
from mind_trader.app.cli.paper_research_cli import run_paper_research_cli
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def write_csv(path):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_paper_research_cli_runs(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    write_csv(folder/"market.csv")
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))

    r=run_paper_research_cli([
        "--data-folder",str(folder),
        "--symbol","TEST",
        "--timeframe","1m",
        "--db-path",str(tmp_path/"m.sqlite"),
        "--ftmo-config",str(cfg),
        "--limit","3"
    ])

    assert r["decision"]=="PAPER_RESEARCH_OPERATION_COMPLETE"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
