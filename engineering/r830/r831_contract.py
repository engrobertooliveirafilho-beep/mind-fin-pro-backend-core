"""R831: offline source inspection. Never import audited modules."""
import ast
from pathlib import Path

PROBES = {"capability_recovery_report", "inspect_capability_module", "_safe_call", "_call_by_signature"}

def audit(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"certified": False, "error": "SYNTAX_ERROR", "line": e.lineno, "findings": []}
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                aliases[a.asname or a.name] = a.name
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                aliases[a.asname or a.name] = (node.module or "") + "." + a.name
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = ast.unparse(node.func)
        root, dot, tail = name.partition(".")
        resolved = aliases.get(root, root) + (dot + tail if dot else "")
        risky = (resolved in {"importlib.import_module", "builtins.__import__", "__import__", "eval", "exec"}
                 or name in PROBES or name in {"fn", "cls"}
                 or name.endswith(".capability_recovery_report")
                 or name.endswith(".inspect_capability_module"))
        if risky:
            findings.append({"line": node.lineno, "call": name, "resolved": resolved})
    return {"certified": False, "error": None,
            "findings": sorted(findings, key=lambda x: x["line"]),
            "static_inspection_complete": True, "active_probe_required": False}

def audit_file(path):
    try:
        return audit(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as e:
        return {"certified": False, "error": type(e).__name__, "findings": []}
