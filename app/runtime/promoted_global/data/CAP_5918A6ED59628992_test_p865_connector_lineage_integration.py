import csv, math
from pathlib import Path
from mind_trader.app.data.market_data_connector import market_data_connector
from mind_trader.app.data.dataset_lineage import verify_lineage

def write_csv(path, rows=120):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(rows):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_connector_generates_lineage_for_approved_dataset(tmp_path):
    p=tmp_path/"data.csv"
    write_csv(p,120)

    r=market_data_connector(
        "GENERIC_OHLCV_CSV",
        p,
        "TEST",
        "1m",
        str(tmp_path/"m.sqlite"),
        str(tmp_path/"catalog.json"),
        str(tmp_path/"lineage.json")
    )

    assert r["decision"]=="DATA_CONNECTED_CATALOGED_LINEAGED"
    assert r["dataset_id"] is not None
    assert len(r["lineage_hash"])==64
    assert r["dataset"]["lineage_hash"]==r["lineage_hash"]
    assert verify_lineage(r["lineage"])["valid"] is True
    assert r["production"]=="BLOCKED"

def test_connector_bad_file_has_no_lineage(tmp_path):
    p=tmp_path/"bad.csv"
    p.write_text("x,y\n1,2\n",encoding="utf-8")

    r=market_data_connector(
        "GENERIC_OHLCV_CSV",
        p,
        "TEST",
        "1m",
        str(tmp_path/"m.sqlite"),
        str(tmp_path/"catalog.json"),
        str(tmp_path/"lineage.json")
    )

    assert r["decision"]=="DATA_BLOCKED"
    assert r["lineage"] is None
    assert r["lineage_hash"] is None

def test_lineage_manifest_written(tmp_path):
    p=tmp_path/"data.csv"
    write_csv(p,120)

    market_data_connector(
        "GENERIC_OHLCV_CSV",
        p,
        "TEST",
        "1m",
        str(tmp_path/"m.sqlite"),
        str(tmp_path/"catalog.json"),
        str(tmp_path/"lineage.json")
    )

    assert Path("mind_trader/reports/P8.65_market_data_connector_lineage_manifest.json").exists()
