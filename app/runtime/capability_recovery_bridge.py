import importlib
import inspect
import ast
from pathlib import Path


TOP5_MODULES = [
    "app.eldora.core.persistent_social_memory",
    "app.persona.adaptive_social_dialogue",
    "app.api.eldora_social",
    "app.retrieval.provider",
    "app.eldora.core.long_term_memory",
]


def _call_by_signature(fn, user_id="default", message=""):
    """Legacy API retained, but arbitrary call execution is forbidden."""
    return {
        "ok": False,
        "skipped": True,
        "reason": "active_probe_disabled",
    }


def inspect_capability_module(module_name: str) -> dict:
    """Legacy API retained, but importing modules for inspection is forbidden."""
    return {
        "module": module_name,
        "import_ok": False,
        "functions": [],
        "classes": [],
        "call_results": {},
        "error": None,
        "skipped": True,
        "reason": "active_probe_disabled",
        "certification": "not_tested",
    }



def _static_module_declarations(module_name: str, source_root) -> dict:
    """Read-only AST inventory; no import, eval, or invocation."""
    result = {"functions": [], "classes": [], "static_inspection": "not_inspected"}
    if module_name not in TOP5_MODULES:
        result["static_inspection"] = "not_allowlisted"
        return result
    try:
        root = Path(source_root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("invalid root")
        target = root.joinpath(*module_name.split('.')).with_suffix('.py')
        relative = target.relative_to(root)
        if any((root / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts) + 1)):
            result["static_inspection"] = "unavailable"
            return result
        if not target.is_file() or not target.resolve().is_relative_to(root):
            result["static_inspection"] = "unavailable"
            return result
        tree = ast.parse(target.read_text(encoding="utf-8"))
        result["functions"] = sorted(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
        result["classes"] = sorted(node.name for node in tree.body if isinstance(node, ast.ClassDef))
        result["static_inspection"] = "parsed_not_executed"
    except (OSError, UnicodeError, SyntaxError, ValueError):
        result["static_inspection"] = "unavailable"
    return result

def capability_recovery_report(user_id: str = "default", message: str = "", *, execute_probes: bool = False, source_root=None) -> dict:
    """Declared-only inventory; legacy active probing is disabled even on opt-in."""
    modules = []
    for module_name in TOP5_MODULES:
        item = inspect_capability_module(module_name)
        if source_root is not None:
            item.update(_static_module_declarations(module_name, source_root))
        modules.append(item)
    return {
        "bridge": "P4.72D_ASYNC_SAFE_CAPABILITY_BRIDGE",
        "user_id": user_id,
        "message": message,
        "mode": "declared_only",
        "active_probe_requested": execute_probes is True,
        "active_probe_allowed": False,
        "modules": modules,
        "summary": {
            "total": len(TOP5_MODULES),
            "import_ok": 0,
            "with_successful_calls": 0,
            "skipped_async": 0,
            "skipped_active_probes": len(TOP5_MODULES),
            "functionally_certified": 0,
        },
    }
