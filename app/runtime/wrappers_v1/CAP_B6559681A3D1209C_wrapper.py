
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_B6559681A3D1209C"
SOURCE_FILE=r"""_quarantine\P19P38_L_SAFE_JUNK_QUARANTINE_20260622_182732\_institutional__\P1903B_EVENT_SOURCE_REGISTRY\event_source_registry.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_v1\trader\CAP_B6559681A3D1209C_event_source_registry.py"""

def safety_contract():
    return {
        "capability_id": CAPABILITY_ID,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "real_execution_allowed": False,
        "runtime_active": True,
        "paper_only": True
    }

def runtime_allowed():
    return False

def execute(*args, **kwargs):
    return {
        "ok": False,
        "route": "OBSERVE_ONLY",
        "reason": "WRAPPER_EXECUTION_DISABLED_UNTIL_INTEGRATION_TEST",
        "capability_id": CAPABILITY_ID,
        "real_execution_allowed": False
    }
