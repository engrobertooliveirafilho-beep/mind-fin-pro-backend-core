def health():
    return {
        "ok": True,
        "status": "stub_active",
        "module": "mind_trader_institutional_gate",
        "mode": "paper_only"
    }

def run_gate(payload=None):
    return {
        "ok": True,
        "status": "stub_active",
        "module": "mind_trader_institutional_gate",
        "mode": "paper_only",
        "payload": payload or {}
    }
