from app.p153_p155_profit_market_data_pipeline.engine import parse_name, br_float, certify, baseline, run

def test_p153_parse_name():
    assert parse_name("WINFUT_F_0_15min.csv")[0]=="WINFUT"
    assert parse_name("WINFUT_F_0_15min.csv")[1]=="M15"

def test_p154_certify_rows():
    rows=[{"symbol":"WIN","date":"x","open":1,"high":2,"low":1,"close":2} for _ in range(60)]
    assert certify(rows)["certified"] is True

def test_p155_baseline_blocks_orders():
    m=run()
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
