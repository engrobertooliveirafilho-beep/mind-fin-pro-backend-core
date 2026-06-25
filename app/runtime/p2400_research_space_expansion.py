
"""
P2400_RESEARCH_SPACE_EXPANSION

Offline research candidate generator.
No runtime promotion.
No broker bridge.
No real orders.
"""

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def safety_contract():
    return {
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "runtime_allowed": False,
        "real_execution_allowed": False,
        "research_only": True,
    }

def rank_candidate(candidate):
    distance=float(candidate.get("mutation_distance", 99))
    priority=float(candidate.get("priority_score", 0))
    dd_focus=1 if candidate.get("dd_reduction_focus") else 0
    return priority - distance*2 + dd_focus*5

def allow_runtime(candidate):
    return False
