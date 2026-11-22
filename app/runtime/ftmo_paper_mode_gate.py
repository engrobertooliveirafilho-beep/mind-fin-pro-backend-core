"""Standalone fail-closed execution-mode boundary; not wired into legacy FTMO runtime."""
from collections.abc import Mapping

class ExecutionModeBlocked(RuntimeError):
    pass

def dispatch_simulated_intent(mode, intent, paper_engine):
    """Only PAPER or DEMO may reach an explicitly supplied offline callable."""
    if type(mode) is not str or mode not in ("PAPER", "DEMO"):
        raise ExecutionModeBlocked("UNAUTHORIZED_EXECUTION_MODE")
    if not isinstance(intent, Mapping) or not intent:
        raise ExecutionModeBlocked("INVALID_SIMULATED_INTENT")
    if not callable(paper_engine):
        raise ExecutionModeBlocked("MISSING_OFFLINE_ENGINE")
    if intent.get("mode") != mode:
        raise ExecutionModeBlocked("INTENT_MODE_MISMATCH")
    if intent.get("live") is not False or intent.get("real_orders") is not False:
        raise ExecutionModeBlocked("LIVE_EXECUTION_FORBIDDEN")
    return paper_engine(dict(intent))
