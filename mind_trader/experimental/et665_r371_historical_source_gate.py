"""ET665.R371: inspect recovered historical P2405E3 without executing it.

Historical scripts can write to hard-coded Windows paths at module import.
Never import, exec, eval or run the recovered script in certification.
"""
import ast,hashlib,json
from pathlib import Path

REQUIRED=("PAPER_ONLY","FORBIDDEN")
def inspect_source(source):
    tree=ast.parse(source)
    assignments={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                assignments[node.targets[0].id]=node.value.value
    if assignments.get("MODE")!="PAPER_ONLY" or assignments.get("REAL_ORDERS")!="FORBIDDEN" or assignments.get("FTMO_REAL")!="FORBIDDEN":
        raise ValueError("historical source lacks explicit paper-only locks")
    import_side_effects=[node.lineno for node in tree.body if isinstance(node,(ast.For,ast.While,ast.With,ast.Try,ast.Expr))]
    if not import_side_effects:
        raise ValueError("unexpected historical source structure")
    return {"status":"STATIC_INSPECTED_NOT_EXECUTED","sha256":hashlib.sha256(source.encode()).hexdigest(),
            "historical_mission":assignments.get("MISSION"),"import_side_effect_lines":import_side_effects,
            "safe_to_import":False,"p2405_historical_e2e_certified":False}

def inspect_file(path):
    return inspect_source(Path(path).read_text(encoding="utf-8"))
