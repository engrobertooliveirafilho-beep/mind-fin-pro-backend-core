from typing import Any, Dict

def assert_runtime_response_parity(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    same = before == after
    return {
        "parity": same,
        "runtime_response_before": before,
        "runtime_response_after": after,
        "response_modified": not same,
        "runtime_authority_preserved": same,
        "status": "PASS" if same else "FAIL",
    }
