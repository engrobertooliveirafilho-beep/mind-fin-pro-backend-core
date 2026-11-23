"""Fail-closed AST gate for forward-looking P2377 lifecycle/router features."""
import ast
from pathlib import Path
FUTURE_FIELDS={"post_mfe_atr","post_mae_atr","post_efficiency","post_followthrough"}
def audit_text(source):
 t=ast.parse(source)
 funcs={n.name:n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 def fields(fn):
  if fn not in funcs:return set()
  return {n.args[0].value for n in ast.walk(funcs[fn]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="get" and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)}
 life=fields("classify_lifecycle")
 score=fields("context_score")
 window=funcs.get("context_window")
 window_future=False
 if window:
  window_future=any(isinstance(n,ast.Constant) and isinstance(n.value,int) and n.value>0 for n in ast.walk(window))
 return {"lifecycle_uses_future_outcomes":bool(life & FUTURE_FIELDS),
 "context_score_uses_future_outcomes":bool(score & FUTURE_FIELDS),
 "future_window_generated":window_future,
 "lookahead_bias_detected":bool(life & FUTURE_FIELDS) or bool(score & FUTURE_FIELDS),
 "causal_signal_certified":False,"paper_execution_allowed":False}
def audit_file(path):return audit_text(Path(path).read_text(encoding="utf-8"))
