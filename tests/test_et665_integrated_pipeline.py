import csv, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.runtime import p2403e_de40_replay_series_builder as p3
from app.runtime import p2404_correlation_analyzer as p4
from app.runtime import p2405f_factory_walk_forward_validation as p5
from app.runtime import p2406_edge_ensemble_optimizer as p6

def ts(day,minute=0):
    return datetime(2026,1,day,10,minute,tzinfo=timezone.utc).isoformat()

def candles():
    return [
      {"timestamp":ts(1,0),"open":100,"high":101,"low":99,"close":100.5,"spread":10},
      {"timestamp":ts(1,15),"open":101,"high":103,"low":100,"close":102,"spread":20},
      {"timestamp":ts(1,30),"open":102,"high":104,"low":101,"close":103,"spread":30},
      {"timestamp":ts(1,45),"open":103,"high":104,"low":100,"close":101,"spread":20},
    ]

def spec(**kw):
    d=dict(symbol="DE40",point_size=.01,contract_size=1,profit_to_account_fx=1,
      account_currency="EUR",profit_currency="EUR",volume_min=.1,volume_max=10,
      volume_step=.1,commission_per_lot_per_side=0,slippage_points_per_side=2,
      conversion_adjustment_rate=0,financing_per_lot_per_day=0,price_basis="BID")
    d.update(kw); return p3.ContractSpec(**d)

def test_canonical_ohlc_5000_rows_valid():
    path=ROOT/"mind_trader/data/raw/mt5/MT5_GER40_M15_raw.csv"
    rows=list(csv.DictReader(open(path,encoding="utf-8")))
    assert len(rows)==5000
    assert rows[0]["time"]=="2026-03-27 10:30:00"
    assert rows[-1]["time"]=="2026-06-19 21:45:00"
    parsed=[{"timestamp":r["time"],"open":r["open"],"high":r["high"],"low":r["low"],
             "close":r["close"],"spread":r["spread"]} for r in rows]
    assert len(p3.validate_candles(parsed))==5000

def test_candles_require_strict_order_and_valid_ohlc():
    with pytest.raises(ValueError): p3.validate_candles(candles()[::-1])
    bad=candles(); bad[1]["high"]=99
    with pytest.raises(ValueError): p3.validate_candles(bad)

def test_replay_uses_real_signal_next_bar_and_spread_costs():
    signal={"edge_id":"E1","signal_time":ts(1,0),"exit_time":ts(1,30),
      "side":"BUY","stop_price":99,"exit_price":103}
    t=p3.build_trade_candidates(candles(),[signal],spec())[0]
    assert t["entry_time"]==ts(1,15)
    assert t["entry_fill"]==101+.20+.02
    assert t["exit_fill"]==103-.02
    assert t["spread_cost_per_lot"]==.20
    assert t["slippage_cost_per_lot"]==.04
    assert t["net_pnl_per_lot"]<t["gross_pnl_per_lot"]

def test_replay_rejects_missing_or_noncausal_signal_fields():
    with pytest.raises(ValueError):
        p3.build_trade_candidates(candles(),[{"edge_id":"E1","signal_time":ts(1,0),
          "exit_time":ts(1,30),"side":"BUY","stop_price":99}],spec())
    with pytest.raises(ValueError):
        p3.build_trade_candidates(candles(),[{"edge_id":"E1","signal_time":ts(1,45),
          "exit_time":ts(1,30),"side":"BUY","stop_price":99,"exit_price":101}],spec())

def make_trade(eid,en,ex,net=10,risk=100):
    return {"edge_id":eid,"entry_time":en,"exit_time":ex,"risk_per_lot":risk,
      "net_pnl_per_lot":net,"volume_min":.1,"volume_max":10,"volume_step":.1,
      "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
      "real_execution_allowed":False}

def test_simultaneous_positions_obey_open_risk_and_size_lots():
    trades=[make_trade("A",ts(1,0),ts(1,30),10,100),make_trade("B",ts(1,0),ts(1,45),-10,100)]
    summary,ledger,rejected=p5.replay_portfolio(trades,10000,.01,.015)
    assert len(ledger)==2 and not rejected
    assert sum(x["risk_cash"] for x in ledger if x["entry_time"]==ts(1,0))<=150+1e-8
    assert summary["max_concurrent_positions"]==2

def test_portfolio_rejects_real_order_flags():
    t=make_trade("A",ts(1,0),ts(1,30)); t["real_execution_allowed"]=True
    with pytest.raises(ValueError): p5.replay_portfolio([t])

def test_synchronized_daily_returns_zero_when_flat_and_correlation_bounded():
    ledger=[
      {"edge_id":"A","exit_time":ts(1,30),"pnl_cash":100,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"},
      {"edge_id":"B","exit_time":ts(1,45),"pnl_cash":50,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}]
    series=p4.daily_returns(ledger,["2026-01-01","2026-01-02"],10000)
    assert series["A"]["2026-01-02"]==0
    matrix,pairs=p4.correlation_matrix(series,min_observations=1)
    assert -1<=matrix["A"]["B"]<=1

def test_walk_forward_is_chronological_and_embargoed():
    rows=[]; start=datetime(2026,1,1,tzinfo=timezone.utc)
    for i in range(120):
        en=start+timedelta(minutes=15*i); ex=en+timedelta(minutes=30)
        rows.append(make_trade("A",en.isoformat(),ex.isoformat(),2,1))
    result=p5.walk_forward(rows,3,.5,5,1,1,45)
    assert len(result)==3
    for fold in result:
        assert datetime.fromisoformat(fold["train_end"])<datetime.fromisoformat(fold["test_end"])
        assert fold["embargo_minutes"]==45

def member(eid,family,direction="BUY",weight=.34,session="EU",regime="TREND",tf="M15"):
    return {"edge_id":eid,"family":family,"direction":direction,"ensemble_weight":weight,
      "status":"ENSEMBLE_MEMBER","session":session,"regime":regime,"timeframe":tf}

CTX={"session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY"}

def test_contextual_quorum_approves_diverse_consensus():
    d=p6.build_ensemble([member("1","A"),member("2","B"),member("3","C")],3,.62,.4).vote(CTX)
    assert d.allowed and d.votes==3 and d.family_concentration<=.4

def test_context_mismatch_and_incomplete_context_block():
    members=[member("1","A"),member("2","B"),member("3","C")]
    d=p6.build_ensemble(members).vote({})
    assert not d.allowed and d.reason=="CONTEXT_INCOMPLETE"
    members[-1]=member("3","C",session="US")
    d=p6.build_ensemble(members).vote(CTX)
    assert not d.allowed and d.reason=="QUORUM_NOT_REACHED"

def test_family_concentration_and_opposing_vote_block():
    members=[member("1","A",weight=.5),member("2","A",weight=.3),member("3","B",weight=.2)]
    d=p6.build_ensemble(members,3,.6,.4).vote(CTX)
    assert not d.allowed and d.reason=="FAMILY_CONCENTRATION_EXCEEDED"
    members=[member("1","A","SELL",.4),member("2","B","BUY",.3),member("3","C","BUY",.3)]
    d=p6.build_ensemble(members,3,.7,.4).vote(CTX)
    assert not d.allowed and d.reason=="CONFIDENCE_BELOW_GATE"

def test_p2406_never_enables_runtime():
    assert p6.runtime_allowed() is False
    assert p6.build_ensemble([]).vote(CTX).route=="OBSERVE_ONLY"

def test_sell_sizing_requires_stop_side_spread_and_includes_costs():
    signal={"edge_id":"E2","signal_time":ts(1,0),"exit_time":ts(1,30),
            "side":"SELL","stop_price":104,"exit_price":102}
    t=p3.build_trade_candidates(candles(),[signal],spec())[0]
    assert t["spread_cost_per_lot"]==.30
    assert t["risk_per_lot"]>(104-101)
    with pytest.raises(ValueError):
        p3.build_trade_candidates(candles(),[signal],spec(stop_spread_points=None))

def test_actual_p2406_roster_cannot_reach_contextual_quorum():
    roster_path=ROOT/"tests/fixtures/p2406_ensemble_roster.csv"
    roster=list(csv.DictReader(open(roster_path,encoding="utf-8")))
    contexts={(r["session"],r["regime"],r["timeframe"]) for r in roster}
    assert len(contexts)==len(roster)==9
    for session,regime,timeframe in contexts:
        ctx={"session":session,"regime":regime,"timeframe":timeframe,"direction":"BUY"}
        d=p6.build_ensemble(roster,3,.62,.40).vote(ctx)
        assert not d.allowed and d.votes==1 and d.reason=="QUORUM_NOT_REACHED"
        d=p6.build_ensemble(roster,1,.62,.40).vote(ctx)
        assert not d.allowed and d.reason=="FAMILY_CONCENTRATION_EXCEEDED"

def test_ohlc_accepts_original_mt5_time_column():
    rows=[{**row,"time":row["timestamp"]} for row in candles()]
    for row in rows: row.pop("timestamp")
    assert len(p3.validate_candles(rows))==4

def test_currency_conversion_uses_last_completed_fx_bar_without_lookahead():
    signal={"edge_id":"E3","signal_time":ts(1,0),"exit_time":ts(1,30),
            "side":"BUY","stop_price":99,"exit_price":103}
    fx=[{"timestamp":ts(1,15),"close":1.12},{"timestamp":ts(1,30),"close":1.99}]
    s=spec(account_currency="USD",profit_currency="EUR",profit_to_account_fx=None,
           conversion_adjustment_rate=.007)
    t=p3.build_trade_candidates(candles(),[signal],s,fx_candles=fx)[0]
    assert t["profit_to_account_fx"]==1.12
    assert t["fx_source_timestamp"]==ts(1,30)
    with pytest.raises(ValueError):
        p3.build_trade_candidates(candles(),[signal],s,fx_candles=None)

def test_canonical_eurusd_m15_fx_source():
    path=ROOT/"mind_trader/data/raw/mt5/MT5_EURUSD_M15_raw.csv"
    rows=list(csv.DictReader(open(path,encoding="utf-8")))
    assert len(rows)==5000
    assert rows[0]["time"]=="2026-04-08 22:00:00"
    assert rows[-1]["time"]=="2026-06-19 23:45:00"
    rate,source=p3._causal_fx_rate(rows,datetime.fromisoformat("2026-06-19T21:45:00"),15)
    assert rate is not None and source=="2026-06-19T21:30:00"
