import csv, math
from pathlib import Path
from mind_trader.app.data.batch_market_ingestion import batch_ingest_market_folder, infer_source_type

def write_good(path):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(120):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def write_bad(path):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["x","y"]); w.writerow([1,2])

def test_infer_source_type():
    assert infer_source_type("abc_mt5.csv")=="MT5_CSV"
    assert infer_source_type("abc_profit.csv")=="PROFIT_CSV"
    assert infer_source_type("abc.csv")=="GENERIC_OHLCV_CSV"

def test_batch_blocks_missing_folder(tmp_path):
    r=batch_ingest_market_folder(tmp_path/"missing","TEST","1m",str(tmp_path/"m.sqlite"))
    assert r["decision"]=="BATCH_BLOCKED_FOLDER_NOT_FOUND"

def test_batch_ingests_good_and_blocks_bad(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    write_good(folder/"good.csv")
    write_bad(folder/"bad.csv")
    r=batch_ingest_market_folder(folder,"TEST","1m",str(tmp_path/"m.sqlite"))
    assert r["decision"]=="BATCH_COMPLETED"
    assert r["connected"]==1
    assert r["blocked"]==1
    assert r["production"]=="BLOCKED"

def test_batch_manifest_written(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    write_good(folder/"good.csv")
    batch_ingest_market_folder(folder,"TEST","1m",str(tmp_path/"m.sqlite"))
    assert Path("mind_trader/reports/P8.60_batch_market_ingestion_manifest.json").exists()
