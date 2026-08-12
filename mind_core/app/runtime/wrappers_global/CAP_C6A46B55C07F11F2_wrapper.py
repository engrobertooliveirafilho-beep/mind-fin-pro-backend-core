
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_C6A46B55C07F11F2"
DOMAIN="TRADER"
SOURCE_FILE=r"""mind_trader\p56g30c_final_rollback_sql.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\trader\CAP_C6A46B55C07F11F2_p56g30c_final_rollback_sql.py"""

def safety_contract():
    return {
        "capability_id": CAPABILITY_ID,
        "domain": DOMAIN,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "runtime_active": True,
        "paper_only": True,
        "real_execution_allowed": False
    }

def runtime_allowed():
    return False

def execute(*args, **kwargs):
    return {
        "ok": False,
        "route": "OBSERVE_ONLY",
        "reason": "GLOBAL_WRAPPER_EXECUTION_DISABLED_UNTIL_SWITCHBOARD",
        "capability_id": CAPABILITY_ID,
        "domain": DOMAIN,
        "real_execution_allowed": False
    }
