import ast
import inspect
import json
import textwrap
from pathlib import Path

import app.companionship.safe_recovery_adapter as m

p = Path("app/companionship/safe_recovery_adapter.py")
src = p.read_text(encoding="utf-8", errors="ignore")

tree = ast.parse(src)
returns = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "score_memory_relevance":
        for sub in ast.walk(node):
            if isinstance(sub, ast.Return):
                returns.append({
                    "line": sub.lineno,
                    "value": ast.unparse(sub.value)[:1000]
                })

print("=== SCORE SOURCE ===")
print(textwrap.dedent(inspect.getsource(m.score_memory_relevance)))

print("\n=== RETURNS ===")
print(json.dumps(returns, ensure_ascii=False, indent=2))

Path("_evidence/P19P36M_H3_FORENSIC_RETURN_PATH_AUDIT_20260621_233752/score_memory_relevance_source.txt").write_text(
    textwrap.dedent(inspect.getsource(m.score_memory_relevance)),
    encoding="utf-8"
)

Path("_evidence/P19P36M_H3_FORENSIC_RETURN_PATH_AUDIT_20260621_233752/score_memory_relevance_returns.json").write_text(
    json.dumps(returns, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
