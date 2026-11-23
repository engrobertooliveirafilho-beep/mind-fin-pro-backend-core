"""Static audit: detect P2397 runtime writes and contradictory certification flags."""
import ast
from pathlib import Path

def audit_source_text(text):
    tree=ast.parse(text)
    runtime_path=False
    write_text=False
    stack_modified_true=False
    for n in ast.walk(tree):
        if isinstance(n,ast.Assign):
            val=ast.unparse(n.value) if hasattr(ast,"unparse") else ""
            if "app" in val and "runtime" in val:
                runtime_path=True
            if isinstance(n.value,ast.Dict):
                for key,value in zip(n.value.keys,n.value.values):
                    if isinstance(key,ast.Constant) and key.value=="paper_stack_modified" and isinstance(value,ast.Constant) and value.value is True:
                        stack_modified_true=True
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="write_text":
            write_text=True
    return {"runtime_path_declared":runtime_path,"write_text_present":write_text,
      "runtime_mutation_risk":runtime_path and write_text,
      "paper_stack_modified_true":stack_modified_true,
      "historical_no_mutation_claim_supported":not (runtime_path and write_text) and not stack_modified_true,
      "runtime_state_verified":False,"execution_certified":False}
def audit_file(path):
    return audit_source_text(Path(path).read_text(encoding="utf-8"))
