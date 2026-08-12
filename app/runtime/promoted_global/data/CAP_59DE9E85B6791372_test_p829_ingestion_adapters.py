import csv
from pathlib import Path
from mind_trader.app.data.ingestion_adapters import normalize_csv, quality_report, ingest_with_quality_gate, checksum

def write_profit_like(path, duplicate=False, bad=False):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter=";")
        w.writerow(["Data","Abertura","Maxima","Minima","Fechamento","Volume"])
        for i in range(100):
            ts=f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00"
            if duplicate and i==99: ts="2026-01-01T09:01:00"
            o=100+i*0.1; h=o+1; l=o-1; c=o+0.2
            if bad and i==50: h=o-2
            w.writerow([ts,o,h,l,c,1000+i])

def test_checksum_real_file(tmp_path):
    p=tmp_path/"a.csv"; write_profit_like(p)
    assert len(checksum(p))==64

def test_normalize_profit_like_csv(tmp_path):
    p=tmp_path/"profit.csv"; out=tmp_path/"norm.csv"; write_profit_like(p)
    r=normalize_csv(p,out)
    assert r["rows"]==100
    assert out.exists()

def test_quality_blocks_duplicate(tmp_path):
    p=tmp_path/"dup.csv"; out=tmp_path/"norm.csv"; write_profit_like(p,duplicate=True)
    normalize_csv(p,out)
    q=quality_report(out)
    assert q["decision"]=="BLOCK_BACKTEST"
    assert q["duplicates"]==1

def test_quality_blocks_bad_ohlc(tmp_path):
    p=tmp_path/"bad.csv"; out=tmp_path/"norm.csv"; write_profit_like(p,bad=True)
    normalize_csv(p,out)
    q=quality_report(out)
    assert q["decision"]=="BLOCK_BACKTEST"
    assert q["bad_ohlc"]==1

def test_ingest_with_quality_gate_allows_good_file(tmp_path):
    p=tmp_path/"good.csv"; dbp=tmp_path/"m.sqlite"; write_profit_like(p)
    r=ingest_with_quality_gate(p,"TEST","1m",str(dbp),tmp_path/"normalized")
    assert r["decision"]=="INGESTED_AND_BACKTEST_ALLOWED"
    assert r["quality"]["quality_passed"] is True
