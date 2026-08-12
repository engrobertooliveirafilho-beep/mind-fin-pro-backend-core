import csv, math
from pathlib import Path
from mind_trader.app.data.market_data_connector import market_data_connector
from mind_trader.app.data.data_catalog import load_catalog

def write_csv(path, rows=120):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(rows):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_connector_registers_dataset_when_quality_passes(tmp_path):
    p=tmp_path/"data.csv"
    dbp=tmp_path/"m.sqlite"
    catalog=tmp_path/"catalog.json"
    write_csv(p,120)

    r=market_data_connector("GENERIC_OHLCV_CSV",p,"TEST","1m",str(dbp),str(catalog))

    assert r["decision"]=="DATA_CONNECTED_CATALOGED_LINEAGED"
    assert r["dataset"]["status"]=="APPROVED_FOR_RESEARCH"
    assert len(load_catalog(str(catalog)))==1
    assert r["production"]=="BLOCKED"

def test_connector_blocks_and_does_not_catalog_bad_file(tmp_path):
    p=tmp_path/"bad.csv"
    p.write_text("x,y\n1,2\n",encoding="utf-8")
    dbp=tmp_path/"m.sqlite"
    catalog=tmp_path/"catalog.json"

    r=market_data_connector("GENERIC_OHLCV_CSV",p,"TEST","1m",str(dbp),str(catalog))

    assert r["decision"]=="DATA_BLOCKED"
    assert r["dataset"] is None
    assert load_catalog(str(catalog))==[]

def test_connector_manifest_written(tmp_path):
    p=tmp_path/"data.csv"
    write_csv(p,120)

    market_data_connector("GENERIC_OHLCV_CSV",p,"TEST","1m",str(tmp_path/"m.sqlite"),str(tmp_path/"catalog.json"))

    assert Path("mind_trader/reports/P8.63_market_data_connector_catalog_manifest.json").exists()

