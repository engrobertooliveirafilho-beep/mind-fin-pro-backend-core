
"""
P2402_CONTEXT_DIVERSITY_CLUSTERING

Structural diversity selector.
It does not measure temporal correlation.
It does not allow runtime execution.
"""

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def runtime_allowed():
    return False

def structural_key(edge):
    return "|".join([
        str(edge.get("session","UNKNOWN")),
        str(edge.get("footprint","UNKNOWN")),
        str(edge.get("lifecycle","UNKNOWN")),
        str(edge.get("cycle_transition","UNKNOWN")),
        str(edge.get("direction","UNKNOWN")),
    ])

def family_key(edge):
    return "|".join([
        str(edge.get("session","UNKNOWN")),
        str(edge.get("footprint","UNKNOWN")),
        str(edge.get("lifecycle","UNKNOWN")),
    ])

def safety_contract():
    return {
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "runtime_allowed": False,
        "real_execution_allowed": False,
        "correlation_measured": False,
    }
