
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_C6A56AEACD9867B9"
DOMAIN="API"
SOURCE_FILE=r"""_evidence\P4.91L2_STAGING_COPY_AND_TEST_20260623_170841\staging\e4c58c45afa305d558af3c9a8ea8a9e296bfbc4b06d45695dd5ce90beb26e9c6_mind_call_router.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\api\CAP_C6A56AEACD9867B9_e4c58c45afa305d558af3c9a8ea8a9e296bfbc4b06d45695dd5ce90beb26e9c6_mind_call_router.py"""

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
