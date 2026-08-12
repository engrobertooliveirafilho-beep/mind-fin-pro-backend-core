
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_9BE052DA1066E878"
DOMAIN="API"
SOURCE_FILE=r"""_evidence\_drive_recovered_semantic_diamond_runtime_v2\app_embeddings_internal_embeddings_step454_engine.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\api\CAP_9BE052DA1066E878_app_embeddings_internal_embeddings_step454_engine.py"""

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
