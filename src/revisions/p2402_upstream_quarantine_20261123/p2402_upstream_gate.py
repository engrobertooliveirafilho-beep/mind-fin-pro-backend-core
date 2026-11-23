"""P2402 upstream validity gate. Structural taxonomy only; never certify performance."""
import ast
from pathlib import Path
def audit_source(path):
 t=ast.parse(Path(path).read_text(encoding="utf-8"))
 names={n.id for n in ast.walk(t) if isinstance(n,ast.Name)}
 attrs={n.attr for n in ast.walk(t) if isinstance(n,ast.Attribute)}
 strings={n.value for n in ast.walk(t) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
 reads_p2401=any(isinstance(n,ast.Constant) and isinstance(n.value,str) and "P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER" in n.value for n in ast.walk(t))
 metric_reads=bool({"pf","winrate","expectancy","max_dd_r","samples","passed_windows"} & strings)
 quality_uses_metrics="quality_score" in names and metric_reads
 runtime_write=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="write_text" for n in ast.walk(t)) and "runtime" in strings
 return {"p2401_dependency":reads_p2401,"quality_uses_performance_metrics":quality_uses_metrics,
         "runtime_write_present":runtime_write,"structural_taxonomy_only":True,
         "selected_pool_performance_valid":False,"correlation_valid":False,
         "runtime_promotion_allowed":False}
def certify(path):
 r=audit_source(path)
 r["upstream_performance_invalidated"]=r["p2401_dependency"] and r["quality_uses_performance_metrics"]
 r["p2402_performance_certified"]=False
 return r
