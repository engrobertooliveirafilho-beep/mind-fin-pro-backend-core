
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_5A1585D6C275D28B"
SOURCE_FILE=r"""mind_trader\app\p11_data_coverage_engine\engine.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_v1\trader\CAP_5A1585D6C275D28B_engine.py"""

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
