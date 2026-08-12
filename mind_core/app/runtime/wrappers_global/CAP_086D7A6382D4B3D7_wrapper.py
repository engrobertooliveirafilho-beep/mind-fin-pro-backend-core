
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
CAPABILITY_ID="CAP_086D7A6382D4B3D7"
DOMAIN="SOCIAL"
SOURCE_FILE=r""".venv\Lib\site-packages\httpx\_content.py"""
PROMOTED_FILE=r"""C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\app\runtime\promoted_global\social\CAP_086D7A6382D4B3D7__content.py"""

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
