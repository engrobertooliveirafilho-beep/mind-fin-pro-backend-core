import csv
from app.p152_profit_backtest_export_normalizer.engine import map_columns, normalize_file, run

def test_p152_map_portuguese_columns():
    m=map_columns(["Estratégia","Ativo","Fator de Lucro","Drawdown","Taxa de Acerto","Operações","Payoff"])
    assert m["strategy_id"]=="Estratégia"
    assert m["profit_factor"]=="Fator de Lucro"

def test_p152_normalize_file(tmp_path):
    p=tmp_path/"profit.csv"
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["Estratégia","Ativo","Período","Fator de Lucro","Drawdown","Taxa de Acerto","Operações","Payoff"])
        w.writerow(["s1","WIN","M1","1.5","1000","55","200","0.4"])
    r=normalize_file(p)
    assert r["rows"][0]["strategy_id"]=="s1"
    assert r["rows"][0]["profit_factor"]=="1.5"

def test_p152_manifest():
    m=run()
    assert m["STATUS"]=="P15.2_PROFIT_BACKTEST_EXPORT_NORMALIZER_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
