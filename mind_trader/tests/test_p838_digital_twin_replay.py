import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv, load_ohlcv
from mind_trader.app.backtest.digital_twin_replay import replay_sma_execution, apply_synthetic_shock, compare_replay_vs_backtest, digital_twin_report, save_digital_twin_report

def write_csv(path):
    p=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            p += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.3,p-0.3,p,1000+i])

def seed(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; write_csv(p); ingest_ohlcv_csv(p,"TEST","1m",str(dbp)); return dbp

def test_replay_runs_with_ledger(tmp_path):
    dbp=seed(tmp_path)
    rows=load_ohlcv("TEST","1m",str(dbp))
    ledger=tmp_path/"replay.jsonl"
    r=replay_sma_execution(rows,ledger_path=str(ledger))
    assert r["status"]=="REPLAY_DONE"
    assert r["production"]=="BLOCKED"
    assert ledger.exists()

def test_synthetic_shock_marks_event(tmp_path):
    dbp=seed(tmp_path)
    rows=load_ohlcv("TEST","1m",str(dbp))
    shocked=apply_synthetic_shock(rows,shock_index=10,shock_pct=-0.1)
    assert shocked[10]["synthetic_event"]=="EXTREME_SHOCK"
    assert shocked[10]["close"] < rows[10]["close"]

def test_compare_replay_vs_backtest_research_only(tmp_path):
    dbp=seed(tmp_path)
    r=compare_replay_vs_backtest("TEST","1m",str(dbp))
    assert r["decision"]=="RESEARCH_COMPARISON_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_digital_twin_report_blocks_production(tmp_path):
    dbp=seed(tmp_path)
    r=digital_twin_report("TEST","1m",str(dbp))
    assert r["decision"]=="DIGITAL_TWIN_REPLAY_ONLY"
    assert r["production"]=="BLOCKED"
    assert "normal" in r and "shocked" in r

def test_insufficient_data_replay_blocked():
    r=replay_sma_execution([])
    assert r["status"]=="INSUFFICIENT_DATA"

def test_save_digital_twin_report(tmp_path):
    out=save_digital_twin_report({"ok":True},str(tmp_path/"dt.json"))
    assert Path(out).exists()


def test_closed_trade_commissions_reconcile(tmp_path, monkeypatch):
    import json
    from mind_trader.app.backtest import digital_twin_replay as replay
    rows = [{"ts": str(i), "close": price} for i, price in enumerate([100, 100, 100, 110, 110, 110, 110, 110])]
    monkeypatch.setattr(replay, "sma", lambda closes, period: [0, 2, 2, 0, 0, 0, 0, 0] if period == 2 else [1]*8)
    ledger = tmp_path / "commission.jsonl"
    result = replay.replay_sma_execution(rows, fast=2, slow=3, initial_capital=1000, commission=2, ledger_path=str(ledger))
    assert len(result["trades"]) == 1
    assert result["trades"][0]["pnl"] == 6
    assert result["final_equity"] == 1006
    events = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert [event["type"] for event in events] == ["ENTRY", "EXIT"]
    assert events[1]["pnl"] == result["final_equity"] - 1000
