import ast
from pathlib import Path

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")
tree = ast.parse(src)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "eldora_primary_runtime_reply":
        target = node
        break

if not target:
    raise SystemExit("FUNCTION_NOT_FOUND")

print("FUNCTION:", target.name)
print("START_LINE:", target.lineno)
print("END_LINE:", target.end_lineno)

returns = []
for node in ast.walk(target):
    if isinstance(node, ast.Return):
        returns.append((node.lineno, ast.get_source_segment(src, node) or ""))

returns = sorted(returns)

print("\nRETURNS:")
for line, text in returns:
    print(f"LINE {line}: {text[:300].replace(chr(10),' ')}")

# Heurística: primeiro return em indent do corpo principal depois do pipeline
lines = src.splitlines()
for idx, line in enumerate(lines, start=1):
    if "return _p19p9_universal_whatsapp_output_guard(inbound_text, visible.get(\"answer\",\"\"" in line:
        print("\nPRIMARY_PIPELINE_RETURN_LINE:", idx)
        break

print("\nPOST_RETURN_AREA_SAMPLE:")
for i in range(idx, min(idx + 80, len(lines))):
    print(f"{i+1}: {lines[i]}")
