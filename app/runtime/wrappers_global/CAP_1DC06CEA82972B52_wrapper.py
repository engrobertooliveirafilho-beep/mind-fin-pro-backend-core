
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_1DC06CEA82972B52"
DOMAIN="REASONING"
SOURCE_FILE=r"""_evidence\P4.91L2_STAGING_COPY_AND_TEST_20260623_170841\staging\27b0ecf9547f12d9b82cdf88d7bf79edae16d40617bd39df1dba24ef47cd4025_routes_mind_supabase_debug.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\reasoning\CAP_1DC06CEA82972B52_27b0ecf9547f12d9b82cdf88d7bf79edae16d40617bd39df1dba24ef47cd4025_routes_mind_supabase_debug.py"""

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
