
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_4EB4384309BA4AA0"
SOURCE_FILE=r"""mind_trader\tests\test_p8100_paper_research_v1_release.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_v1\trader\CAP_4EB4384309BA4AA0_test_p8100_paper_research_v1_release.py"""

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
