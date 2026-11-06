"""Institutional guard: deny live, production and unrecognized actions.

No order payload is persisted. Audit persistence is best-effort and cannot
turn a denied action into an allowed one.
"""
import json
from pathlib import Path
from datetime import datetime, UTC

FORBIDDEN_ACTIONS = frozenset({
    "LIVE_TRADE",
    "PRODUCTION_TRADE",
    "REAL_MONEY_TRADE",
    "FTMO_REAL_TRADE",
    "BROKER_SEND_ORDER",
    "ENABLE_LIVE_ROUTING",
    "PRODUCTION_APPROVAL",
})

# Explicit research-only actions; extend only after a separate security review.
ALLOWED_RESEARCH_ACTIONS = frozenset({"PAPER", "REPLAY", "MICRO_SIM"})


def institutional_live_lock(action, payload=None):
    """Fail closed for forbidden or unknown actions; never persist raw payload."""
    known_research = isinstance(action, str) and action in ALLOWED_RESEARCH_ACTIONS
    blocked = not known_research
    decision = (
        "FORCE_BLOCK_LIVE_OR_PRODUCTION"
        if action in FORBIDDEN_ACTIONS
        else "BLOCK_UNKNOWN_ACTION"
        if blocked
        else "ALLOW_NON_LIVE_RESEARCH_ACTION"
    )
    report = {
        "lock": "P8.92_INSTITUTIONAL_LIVE_LOCK",
        "created_at": datetime.now(UTC).isoformat(),
        "action": action if isinstance(action, str) else "<INVALID_ACTION>",
        "payload_redacted": True,
        "blocked": blocked,
        "decision": decision,
        "production": "BLOCKED",
        "live": "FORBIDDEN",
        "edge_claim": "NONE",
    }
    try:
        path = Path("mind_trader/reports/P8.92_institutional_live_lock.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        report["audit_persisted"] = True
    except OSError:
        # Read-only filesystems must never bypass the institutional lock.
        report["audit_persisted"] = False
    return report


def assert_not_live_action(action):
    report = institutional_live_lock(action)
    return not report["blocked"], report["decision"]
