"""Static provenance audit for P2400/P2401. No source execution."""
import ast
from pathlib import Path

def inspect(path):
    text=Path(path).read_text(encoding="utf-8")
    tree=ast.parse(text)
    calls={n.func.id if isinstance(n.func,ast.Name) else n.func.attr
           for n in ast.walk(tree) if isinstance(n,ast.Call)}
    imports={a.name for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))
             for a in (n.names if isinstance(n,ast.Import) else [])}
    identifiers={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    literals=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
    writes_runtime=any(x in literals for x in ("runtime","app")) and "write_text" in calls
    hash_derived=bool({"sha256","stable_float"} & calls) or "hashlib" in imports
    price_input=bool({"open","high","low","close","bid","ask","ohlc"} & identifiers)
    metrics_generated=bool({"pf","wr","exp","dd","samples","passed_windows"} & identifiers)
    return {"hash_derived_metrics":hash_derived,"price_or_trade_data_inputs_referenced":price_input,
      "performance_metrics_generated":metrics_generated,"runtime_write_pattern":writes_runtime,
      "performance_evidence_certified":False,"promotion_allowed":False}

def audit(p2400,p2401):
    a,b=inspect(p2400),inspect(p2401)
    return {"p2400":a,"p2401":b,
      "p2401_metrics_are_synthetic":b["hash_derived_metrics"] and b["performance_metrics_generated"] and not b["price_or_trade_data_inputs_referenced"],
      "p2400_paper_stack_mutation_claim":a["runtime_write_pattern"],
      "p2401_performance_certified":False,"p2401_promotions_valid":False,
      "runtime_promotion_allowed":False}
