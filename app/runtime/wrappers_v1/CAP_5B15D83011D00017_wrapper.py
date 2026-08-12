
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_5B15D83011D00017"
SOURCE_FILE=r"""_evidence\P19P38_P_UNTRACKED_MODULE_INVENTORY_20260622_184140\p19p38p_untracked_inventory.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_v1\trader\CAP_5B15D83011D00017_p19p38p_untracked_inventory.py"""

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
