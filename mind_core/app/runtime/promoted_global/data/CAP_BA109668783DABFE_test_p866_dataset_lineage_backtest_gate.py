import csv, math
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.genomes.strategy_genome import make_genome
from mind_trader.app.data.data_catalog import register_dataset
from mind_trader.app.data.dataset_lineage import create_dataset_lineage
from mind_trader.app.data.dataset_lineage_gate import require_dataset_with_lineage
from mind_trader.app.backtest.massive_cluster import run_genome_backtest

def seed(tmp_path, with_lineage=True):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; price=100
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.3,price-0.3,price,1000+i])
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    catalog=tmp_path/"catalog.json"
    lineage=tmp_path/"lineage.json"
    ds=register_dataset("TEST","1m","abc",180,True,str(catalog))
    if with_lineage:
        create_dataset_lineage(ds,{"file_path":str(p),"file_checksum":"abc","db_path":str(dbp),"ingestion_result":{"quality":{"rows":180,"quality_passed":True}}},str(lineage))
    return dbp,catalog,lineage,ds

def test_dataset_lineage_gate_ok(tmp_path):
    dbp,catalog,lineage,ds=seed(tmp_path)
    r=require_dataset_with_lineage(ds["dataset_id"],str(catalog),str(lineage))
    assert r["allowed"] is True
    assert r["decision"]=="DATASET_AND_LINEAGE_OK"

def test_dataset_lineage_gate_blocks_missing_lineage(tmp_path):
    dbp,catalog,lineage,ds=seed(tmp_path,with_lineage=False)
    r=require_dataset_with_lineage(ds["dataset_id"],str(catalog),str(lineage))
    assert r["allowed"] is False
    assert r["decision"]=="BLOCK_LINEAGE_NOT_FOUND"

def test_backtest_blocks_without_valid_lineage(tmp_path):
    dbp,catalog,lineage,ds=seed(tmp_path,with_lineage=False)
    g=make_genome("SMA_CROSS","TEST","1m","TREND_UP",{"fast":5,"slow":21})
    r=run_genome_backtest(g,str(dbp),dataset_id=ds["dataset_id"],catalog_path=str(catalog),lineage_path=str(lineage))
    assert r["status"]=="BLOCKED_DATASET_LINEAGE"

def test_backtest_allows_with_dataset_and_lineage(tmp_path):
    dbp,catalog,lineage,ds=seed(tmp_path,with_lineage=True)
    g=make_genome("SMA_CROSS","TEST","1m","TREND_UP",{"fast":5,"slow":21})
    r=run_genome_backtest(g,str(dbp),dataset_id=ds["dataset_id"],catalog_path=str(catalog),lineage_path=str(lineage))
    assert r["status"] in ["TESTED","FAILED"]
    assert r["production"]=="BLOCKED"
