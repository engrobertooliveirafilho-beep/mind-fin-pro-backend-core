import pandas as pd
from causal_portfolio_engine import CostModel,RiskConfig,replay,validate_events
from p2406_contextual_vote import contextual_vote

def sample():
 return pd.DataFrame([
 {"edge_id":"A","entry_time":pd.Timestamp("2026-01-01 10:00"),"exit_time":pd.Timestamp("2026-01-01 10:30"),"pnl_r":1.0,"holding_bars":2,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","real_execution_allowed":False},
 {"edge_id":"B","entry_time":pd.Timestamp("2026-01-01 10:00"),"exit_time":pd.Timestamp("2026-01-01 11:00"),"pnl_r":-1.0,"holding_bars":4,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","real_execution_allowed":False}])

def test_costs_reduce_net_r():
 _,ledger=replay(sample(),CostModel(.02,.01,.02),RiskConfig())
 assert (ledger.net_r<ledger.gross_r).all()

def test_concurrent_positions_respect_cap():
 summary,ledger=replay(sample(),CostModel(0,0,0),RiskConfig(risk_per_trade=.01,max_open_risk=.015))
 assert ledger.risk_cash.sum()<=150
 assert summary["unclosed_positions"]==0

def test_real_execution_flag_fails_closed():
 df=sample(); df.loc[0,"real_execution_allowed"]=True
 try: validate_events(df)
 except ValueError: return
 assert False

def test_context_mismatch_blocks():
 m=[{"status":"ENSEMBLE_MEMBER","session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY","family":"LIQ","ensemble_weight":.5}]
 d=contextual_vote(m,{"session":"US","regime":"TREND","timeframe":"M15","direction":"BUY"})
 assert not d.allowed and d.reason=="QUORUM_NOT_REACHED"

def test_family_cap_blocks():
 m=[{"status":"ENSEMBLE_MEMBER","session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY","family":"LIQ","ensemble_weight":.4} for _ in range(3)]
 d=contextual_vote(m,{"session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY"},3,.62,.4)
 assert not d.allowed and d.reason=="FAMILY_CONCENTRATION_EXCEEDED"

def test_diverse_contextual_quorum():
 m=[{"status":"ENSEMBLE_MEMBER","session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY","family":f,"ensemble_weight":.34} for f in ["LIQ","MTF","VOL"]]
 d=contextual_vote(m,{"session":"EU","regime":"TREND","timeframe":"M15","direction":"BUY"},3,.62,.4)
 assert d.allowed and d.votes==3
