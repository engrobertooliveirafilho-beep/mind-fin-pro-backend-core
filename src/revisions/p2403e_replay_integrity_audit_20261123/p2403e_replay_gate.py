"""Audit P2403E replay provenance. Detects sampled pseudo-trades, not strategy signals."""
import ast
from pathlib import Path
def audit_source(path):
 t=ast.parse(Path(path).read_text(encoding="utf-8"))
 calls={n.func.id if isinstance(n.func,ast.Name) else n.func.attr for n in ast.walk(t) if isinstance(n,ast.Call)}
 names={n.id for n in ast.walk(t) if isinstance(n,ast.Name)}
 strings={n.value for n in ast.walk(t) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
 subs={n.slice.value for n in ast.walk(t) if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str)}
 uses_hash="sha256" in calls or "hashlib" in names
 synthetic_schedule=bool({"stride","offset","hold"} & names) and "sha256" in calls
 has_signal_rules=bool({"footprint","lifecycle","cycle_transition","session","regime"} & subs)
 has_trade_costs=bool({"spread","slippage","commission","fee"} & subs)
 source_ohlc=("open" in subs and "high" in subs and "low" in subs and "close" in subs)
 return {"hash_based_trade_schedule":synthetic_schedule,"strategy_signal_rules_present":has_signal_rules,
 "canonical_ohlc_fields_read":source_ohlc,"transaction_cost_model_present":has_trade_costs,
 "trade_rows_are_strategy_replay":False,"correlation_ready":False,"performance_certified":False,
 "runtime_promotion_allowed":False}
def validate(path):
 r=audit_source(path)
 r["pseudo_replay_detected"]=r["hash_based_trade_schedule"] and not r["strategy_signal_rules_present"]
 return r
