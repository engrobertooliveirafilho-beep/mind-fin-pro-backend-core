"""Fail-closed Git blob verifier for the isolated PAPER research chain."""
import hashlib
from pathlib import Path

EXPECTED = {
    "p2395_context_router_safe.py":"fa3b8b8a6bbe8fa0198c34decaa61e97177a8526",
    "p2396_ensemble_safe.py":"7a586e8b0875bc00d8d0d646a8a1563c19918415",
    "p2397_historical_bridge.py":"a971d1b25bf37e152bf39e71cc4120f0c1969ed8",
    "p2397_research_gate.py":"33eeab1d11c9258711802015ba4b12c587cc60cd",
    "p2398_historical_chain.py":"49fd286cf44b8c031a31f8aacf55240c0e356ab6",
    "p2398_evidence_adapter.py":"8ed97abad062b9f6e506cd86914ba31a460ba132",
    "p2398_observe_gate.py":"e59d2341e9fc40f71ff80d01da62267ea27a14b1",
    "p2398_research_chain.py":"5aa673bd60fb797e86e62f0deb416891a7721565",
    "router_contract.json":"277466c8b3ab20640086ecc5cfde3fb7d599de63",
    "ensemble_result.json":"b5772fa840ac944c31abc780a83045ebef9325c2",
    "p2394_original_summary.json":"7ddd72209e0d827908e06c3ff031a48a6b3061ea",
    "p2397_original_policy.json":"3c2b31b43fbe45648b6144d7f220c9cbd3cba0b1",
    "p2397_original_summary.json":"993d37dd84bcce72584f2cd7f0e7e38496f0f8be",
    "p2397_original_hypotheses.csv":"8b90b3e666e207415f29726a20f8aba93f552795",
}

def check(base):
    mismatches = []
    for name, expected in EXPECTED.items():
        path = Path(base) / name
        if not path.is_file():
            mismatches.append((name, "MISSING"))
            continue
        data = path.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected:
            mismatches.append((name, actual))
    return mismatches

if __name__ == "__main__":
    issues = check(Path(__file__).resolve().parent)
    print("FILES", len(EXPECTED), "MATCH", len(EXPECTED)-len(issues), "DRIFT", len(issues))
    for name, actual in issues:
        print("DRIFT", name, actual)
    raise SystemExit(1 if issues else 0)
