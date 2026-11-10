"""R379: verify historical unified dispatcher collision without executing it.

Source: Google Drive file 1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-.
The original imports 51 run_dry functions under the same global symbol,
then calls globals()['run_dry'] for any agent_id; its mod variable is unused.
This is a source-level defect, not proof that the historical agents executed.
"""
import ast
from mind_trader.experimental.et665_r340_safe_agent_dispatch import AGENT_MODULES

HISTORICAL_SOURCE_DRIVE_ID = "1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-"
HISTORICAL_DISPATCH = """def run_agent(agent_id: str, payload=None):
    try:
        mod = agent_id.replace('.', '_')
        fn = globals().get('run_dry')
        return fn(payload)
    except Exception as e:
        return {'agent_id': agent_id, 'error': str(e)}
"""

def check_dispatch_source(source):
    tree=ast.parse(source)
    funcs=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name=="run_agent"]
    if len(funcs)!=1:
        raise RuntimeError("expected one historical dispatcher")
    fn=funcs[0]
    calls=[node for node in ast.walk(fn) if isinstance(node,ast.Call)]
    uses_global=any(isinstance(call.func,ast.Attribute) and call.func.attr=="get" and isinstance(call.func.value,ast.Call) and isinstance(call.func.value.func,ast.Name) and call.func.value.func.id=="globals" and call.args and isinstance(call.args[0],ast.Constant) and call.args[0].value=="run_dry" for call in calls)
    imports=[node for node in tree.body if isinstance(node,ast.ImportFrom) and any(alias.name=="run_dry" and alias.asname is None for alias in node.names)]
    return {"global_run_dry_lookup":uses_global,"unaliased_run_dry_imports":len(imports),"collision_risk":uses_global and len(imports)>1}

def audit():
    # Evidence-backed structural fact; does not pretend to re-run the Drive file.
    source=HISTORICAL_DISPATCH
    finding=check_dispatch_source(source)
    if not finding["global_run_dry_lookup"]:
        raise RuntimeError("historical dispatcher signature changed")
    if len(AGENT_MODULES)!=19 or len(set(AGENT_MODULES))!=19:
        raise RuntimeError("candidate manifest invalid")
    return {"status":"HISTORICAL_DISPATCH_DEFECT_IDENTIFIED",
            "source_drive_id":HISTORICAL_SOURCE_DRIVE_ID,
            "dispatcher_ignores_requested_agent":True,
            "source_imports_observed_in_drive":51,
            "source_imports_verified_by_local_ast":False,
            "candidate_dispatch_isolated":True,
            "official_hp19_certified":0,"phase_b_certified":0,
            "real_orders":"FORBIDDEN"}
