from typing import Dict, Any, List

def certify_p10_to_p15(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    failures = [r for r in results if r.get("status") != "PASS"]
    mutations = [
        r for r in results
        if r.get("runtime_state_modified") or r.get("routes_modified") or r.get("dispatcher_modified") or r.get("whatsapp_webhook_modified")
    ]

    return {
        "mission": "P15_FINAL_CONTROLLED_ACTIVATION_CERTIFICATION",
        "total_results": len(results),
        "failures": len(failures),
        "mutations": len(mutations),
        "runtime_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "certification": "PASS" if not failures and not mutations else "FAIL",
        "status": "PASS" if not failures and not mutations else "FAIL",
    }
