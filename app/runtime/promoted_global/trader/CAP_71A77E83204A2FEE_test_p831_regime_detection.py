from pathlib import Path
from mind_trader.app.engines.regime_detection import detect_regime_from_rows, regime_series, require_defined_regime, save_regime_report

def rows_trend(n=80, step=0.2):
    out=[]; p=100
    for i in range(n):
        p+=step
        out.append({"ts":str(i),"open":p-0.1,"high":p+0.3,"low":p-0.3,"close":p,"volume":1000})
    return out

def rows_range(n=80):
    out=[]
    for i in range(n):
        p=100 + ((i%10)-5)*0.03
        out.append({"ts":str(i),"open":p,"high":p+0.2,"low":p-0.2,"close":p,"volume":1000})
    return out

def rows_expansion(n=80):
    out=[]; p=100
    for i in range(n):
        p += 0.1 if i%2 else -0.1
        out.append({"ts":str(i),"open":p,"high":p+4,"low":p-4,"close":p,"volume":1000})
    return out

def test_blocks_insufficient_data():
    r=detect_regime_from_rows(rows_trend(10),window=30)
    assert r["regime"]=="UNDEFINED"
    assert require_defined_regime(r)[0] is False

def test_detects_uptrend():
    r=detect_regime_from_rows(rows_trend(),window=30)
    assert r["regime"] in ["TREND_UP","EXPANSION_HIGH_VOL"]
    assert require_defined_regime(r)[0] is True

def test_detects_downtrend():
    r=detect_regime_from_rows(rows_trend(step=-0.2),window=30)
    assert r["regime"] in ["TREND_DOWN","EXPANSION_HIGH_VOL"]

def test_detects_range_or_compression():
    r=detect_regime_from_rows(rows_range(),window=30)
    assert r["regime"] in ["RANGE_SIDEWAYS","COMPRESSION_LOW_VOL"]

def test_detects_expansion():
    r=detect_regime_from_rows(rows_expansion(),window=30)
    assert r["regime"]=="EXPANSION_HIGH_VOL"

def test_regime_series_len():
    rs=regime_series(rows_trend(80),window=30)
    assert len(rs)==51
    assert "regime" in rs[-1]

def test_save_regime_report(tmp_path):
    out=save_regime_report({"ok":True},str(tmp_path/"regime.json"))
    assert Path(out).exists()
