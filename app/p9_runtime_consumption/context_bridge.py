from typing import Any, Dict

def build_read_only_runtime_context(runtime_input: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "context_type": "READ_ONLY_RUNTIME_CONTEXT",
        "input": dict(runtime_input),
        "read_only": True,
        "runtime_modified": False,
        "state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
    }
