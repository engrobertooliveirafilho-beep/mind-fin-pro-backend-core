import copy
import json
from pathlib import Path
import pytest
from app.runtime.p2299_paper_signal_plan import validate_plan, paper_signal

PLAN = Path(__file__).resolve().parents[1] / "tests/fixtures/p2299_original_signal_plan.json"

@pytest.fixture
def rows():
    return json.loads(PLAN.read_text(encoding="utf-8"))

def test_original_drive_plan_validated(rows):
    result = validate_plan(rows)
    assert result["rows"] == 4 and result["unique_keys"] == 4
    assert result["independent_edges_certified"] == 0 and result["broker_orders"] == 0

@pytest.mark.parametrize("key,bad", [
    ("mode", "LIVE"), ("real_orders", "ALLOWED"), ("ftmo_real", "ALLOWED"),
    ("candle_lock", "OPEN_H1"), ("lot", "1.0"), ("lot", "NaN"),
    ("max_trades_day", 999), ("family", "UNKNOWN"),
])
def test_unsafe_plan_rejected(rows, key, bad):
    rows[0][key] = bad
    with pytest.raises(ValueError): validate_plan(rows)

def test_duplicate_edge_key_rejected(rows):
    rows[1]["dedup_key"] = rows[0]["dedup_key"]
    with pytest.raises(ValueError): validate_plan(rows)

def test_paper_observation_closed_candle(rows):
    result = paper_signal(rows[0], {"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"}, "BUY", seen_keys=set(), daily_count=0, edge_daily_count=0)
    assert result["status"] == "PAPER_OBSERVATION_ONLY"
    assert result["broker_order"] is None

@pytest.mark.parametrize("change", [
    {"closed":False}, {"symbol":"EURUSD"}, {"timeframe":"M5"},
    {"timestamp":"2026-06-22T12:15:00+00:00"},
    {"timestamp":"2026-06-22T12:00:00"},
])
def test_bad_candles_rejected(rows, change):
    candle={"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"}
    candle.update(change)
    with pytest.raises(ValueError): paper_signal(rows[0],candle,"BUY",seen_keys=set(),daily_count=0,edge_daily_count=0)

def test_duplicate_candle_rejected(rows):
    with pytest.raises(ValueError, match="P2299_DUPLICATE_CANDLE"):
        paper_signal(rows[0],{"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"},"BUY",seen_keys={(rows[0]["dedup_key"],"2026-06-22T12:00:00+00:00")},daily_count=0,edge_daily_count=0)

@pytest.mark.parametrize("daily,edge",[(6,0),(0,2)])
def test_daily_limits(rows,daily,edge):
    with pytest.raises(ValueError,match="P2299_DAILY_LIMIT"):
        paper_signal(rows[0],{"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"},"SELL",seen_keys=set(),daily_count=daily,edge_daily_count=edge)

def test_global_candle_lock_blocks_other_edge(rows):
    candle={"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"}
    with pytest.raises(ValueError,match="P2299_DUPLICATE_CANDLE"):
        paper_signal(rows[1],candle,"BUY",seen_keys={("CANDLE","2026-06-22T12:00:00+00:00")},daily_count=1,edge_daily_count=0)

@pytest.mark.parametrize("key,bad", [("lot","100"),("symbol","EURUSD"),("max_trades_day",100),("candle_lock","OPEN_H1")])
def test_direct_signal_cannot_bypass_plan_validation(rows,key,bad):
    rows[0][key]=bad
    candle={"symbol":"GER40","timeframe":"H1","closed":True,"timestamp":"2026-06-22T12:00:00+00:00"}
    with pytest.raises(ValueError):
        paper_signal(rows[0],candle,"BUY",seen_keys=set(),daily_count=0,edge_daily_count=0)
