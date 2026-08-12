import csv, math
from pathlib import Path
from mind_trader.app.data.market_data_connector import market_data_connector

def write_csv(path):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter=";")
        w.writerow(["Data","Abertura","Maxima","Minima","Fechamento","Volume"])
        for i in range(120):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_blocks_unsupported_source(tmp_path):
    r=market_data_connector("API_REAL_TIME",tmp_path/"x.csv","TEST","1m",str(tmp_path/"m.sqlite"))
    assert r["decision"]=="BLOCKED_UNSUPPORTED_SOURCE"

def test_blocks_missing_file(tmp_path):
    r=market_data_connector("MT5_CSV",tmp_path/"missing.csv","TEST","1m",str(tmp_path/"m.sqlite"))
    assert r["decision"]=="BLOCKED_FILE_NOT_FOUND"

def test_connects_profit_csv_real_file(tmp_path):
    p=tmp_path/"profit.csv"; write_csv(p)
    r=market_data_connector("PROFIT_CSV",p,"TEST","1m",str(tmp_path/"m.sqlite"))
    assert r["decision"]=="DATA_CONNECTED_CATALOGED_LINEAGED"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_manifest_written(tmp_path):
    p=tmp_path/"mt5.csv"; write_csv(p)
    market_data_connector("MT5_CSV",p,"TEST","1m",str(tmp_path/"m.sqlite"))
    assert Path("mind_trader/reports/P8.59_market_data_connector_manifest.json").exists()


