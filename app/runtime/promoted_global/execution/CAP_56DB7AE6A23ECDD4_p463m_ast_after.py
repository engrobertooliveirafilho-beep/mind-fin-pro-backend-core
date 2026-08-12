import ast
from pathlib import Path

src = Path("app/api/whatsapp.py").read_text(encoding="utf-8")
tree = ast.parse(src)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "eldora_primary_runtime_reply":
        target = node
        break

print("FUNCTION_START:", target.lineno)
print("FUNCTION_END:", target.end_lineno)

returns = []
for node in ast.walk(target):
    if isinstance(node, ast.Return):
        returns.append(node.lineno)

print("RETURNS:", sorted(returns))
print("P4.63M_AST_AFTER_OK")
