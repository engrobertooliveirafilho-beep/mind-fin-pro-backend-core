"""R830: static, fail-closed audit of legacy capability bridge consumers. No imports."""
import ast
from pathlib import Path

DANGEROUS = {"importlib.import_module", "__import__", "eval", "exec"}
CALLABLE_NAMES = {"_call_by_signature", "inspect_capability_module", "capability_recovery_report"}

def audit_source(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"safe": False, "reason": "syntax_error", "line": exc.lineno, "findings": []}
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        try:
            name = ast.unparse(node.func)
        except Exception:
            name = "<unknown>"
        if name in DANGEROUS or name in CALLABLE_NAMES or name in {"fn", "cls"}:
            findings.append({"line": node.lineno, "call": name, "risk": "dynamic_execution"})
    return {"safe": not findings, "findings": sorted(findings, key=lambda x: (x["line"], x["call"]))}

def audit_paths(paths):
    reports = {}
    for raw in paths:
        path = Path(raw)
        try:
            reports[str(path)] = audit_source(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            reports[str(path)] = {"safe": False, "reason": type(exc).__name__, "findings": []}
    return reports
