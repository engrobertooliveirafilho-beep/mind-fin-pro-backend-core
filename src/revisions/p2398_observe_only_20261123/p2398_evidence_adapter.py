"""Read-only adapter for historical P2395/P2396 JSON evidence. Never dispatches orders."""
from collections.abc import Mapping
from p2398_observe_gate import evaluate, GateRejected

def evaluate_evidence(router: Mapping, ensemble: Mapping) -> dict:
    if not isinstance(router, Mapping) or not isinstance(ensemble, Mapping):
        raise GateRejected("evidence must be mappings")
    expected_router = {"mission": "P2395_CONTEXT_ROUTER_V2",
                       "input_edge_decision": "OBSERVE_SCORE",
                       "route_result": "OBSERVE_ONLY",
                       "integration_mode": "ISOLATED_RUNTIME_MODULE"}
    expected_ensemble = {"vote": "OBSERVE_ONLY",
                         "reason": "INSUFFICIENT_OPERATIONAL_QUORUM"}
    for obj, expected in ((router, expected_router), (ensemble, expected_ensemble)):
        for key, value in expected.items():
            if obj.get(key) != value:
                raise GateRejected(f"invalid evidence {key}")
        for key, value in (("mode", "PAPER_ONLY"), ("real_orders", "FORBIDDEN"),
                           ("ftmo_real", "FORBIDDEN")):
            if obj.get(key) != value:
                raise GateRejected(f"invalid evidence {key}")
    if router.get("real_execution_allowed") is not False:
        raise GateRejected("router execution permission unsafe")
    if ensemble.get("allowed") is not False:
        raise GateRejected("ensemble permission unsafe")
    if type(ensemble.get("members")) is not int or ensemble["members"] != 1:
        raise GateRejected("ensemble membership invalid")
    if type(ensemble.get("operational_members")) is not int or ensemble["operational_members"] != 0:
        raise GateRejected("operational membership invalid")
    if type(ensemble.get("quorum")) is not int or ensemble["quorum"] < 2:
        raise GateRejected("quorum invalid")
    return evaluate({
        "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "p2394_decision": router["input_edge_decision"],
        "p2395_decision": router["route_result"],
        "p2396_vote": ensemble["vote"],
        "real_execution_allowed": False,
        "runtime_modification_allowed": False,
        "operational_members": ensemble["operational_members"],
        "quorum_required": ensemble["quorum"],
    })
