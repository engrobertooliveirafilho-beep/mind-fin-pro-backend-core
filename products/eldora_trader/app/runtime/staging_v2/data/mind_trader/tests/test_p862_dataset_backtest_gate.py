import csv, math
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.genomes.strategy_genome import make_genome
from mind_trader.app.data.data_catalog import register_dataset
from mind_trader.app.data.dataset_lineage import create_dataset_lineage
from mind_trader.app.backtest.massive_cluster import run_genome_backtest, massive_backtest_cluster

def seed(tmp_path):
    p=tmp_path/"ohlcv.csv"
    dbp=tmp_path/"m.sqlite"
    price=100

    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.3 + 0.05
            w.writerow([
                f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",
                price-0.1,
                price+0.3,
                price-0.3,
                price,
                1000+i
            ])

    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))

    catalog=tmp_path/"catalog.json"
    lineage=tmp_path/"lineage.json"

    ds=register_dataset("TEST","1m","abc",180,True,str(catalog))

    create_dataset_lineage(
        ds,
        {
            "file_path":str(p),
            "file_checksum":"abc",
            "db_path":str(dbp),
            "ingestion_result":{
                "quality":{
                    "rows":180,
                    "quality_passed":True
                }
            }
        },
        str(lineage)
    )

    return dbp,catalog,ds,lineage

def test_backtest_blocks_missing_dataset(tmp_path):
    dbp,catalog,ds,lineage=seed(tmp_path)

    g=make_genome(
        "SMA_CROSS",
        "TEST",
        "1m",
        "TREND_UP",
        {"fast":5,"slow":21}
    )

    r=run_genome_backtest(
        g,
        str(dbp),
        dataset_id="missing",
        catalog_path=str(catalog),
        lineage_path=str(lineage)
    )

    assert r["status"]=="BLOCKED_DATASET_LINEAGE"

def test_backtest_allows_approved_dataset(tmp_path):
    dbp,catalog,ds,lineage=seed(tmp_path)

    g=make_genome(
        "SMA_CROSS",
        "TEST",
        "1m",
        "TREND_UP",
        {"fast":5,"slow":21}
    )

    r=run_genome_backtest(
        g,
        str(dbp),
        dataset_id=ds["dataset_id"],
        catalog_path=str(catalog),
        lineage_path=str(lineage)
    )

    assert r["status"] in ["TESTED","FAILED"]
    assert r["production"]=="BLOCKED"

def test_cluster_blocks_all_with_missing_dataset(tmp_path):
    dbp,catalog,ds,lineage=seed(tmp_path)

    gs=[
        make_genome(
            "SMA_CROSS",
            "TEST",
            "1m",
            "TREND_UP",
            {"fast":5,"slow":21}
        )
    ]

    r=massive_backtest_cluster(
        gs,
        str(dbp),
        dataset_id="missing",
        catalog_path=str(catalog),
        lineage_path=str(lineage)
    )

    assert r["blocked"]==1
    assert r["tested"]==0
