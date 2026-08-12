
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_458375241AA8C074"
DOMAIN="TRADER"
SOURCE_FILE=r"""_evidence\P4.82G_P479_KNOWLEDGE_EXTRACTION_RECOVERY_20260621_114957\p482g_patch_knowledge_extractor.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\trader\CAP_458375241AA8C074_p482g_patch_knowledge_extractor.py"""

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
