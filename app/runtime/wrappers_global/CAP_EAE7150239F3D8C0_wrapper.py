
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_EAE7150239F3D8C0"
DOMAIN="API"
SOURCE_FILE=r"""_evidence\P4.91L2_STAGING_COPY_AND_TEST_20260623_170841\staging\2a0bff0e5fbbc203ddbcc34b4fbc4e168359b7454277fde28fb8a9a4910e7a33_steps_planned_batch_0002.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\api\CAP_EAE7150239F3D8C0_2a0bff0e5fbbc203ddbcc34b4fbc4e168359b7454277fde28fb8a9a4910e7a33_steps_planned_batch_0002.py"""

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
