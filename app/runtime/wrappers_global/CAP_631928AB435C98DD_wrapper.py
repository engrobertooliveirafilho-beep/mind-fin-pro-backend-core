
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_631928AB435C98DD"
DOMAIN="EXECUTION"
SOURCE_FILE=r"""_evidence\P4_63J_EXPAND_CONTINUITY_INTENT_20260618_124829\p463j_smoke.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\execution\CAP_631928AB435C98DD_p463j_smoke.py"""

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
