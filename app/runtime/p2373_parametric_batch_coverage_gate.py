"""P2373 batch evidence gate: partial parametric sweeps are not certified coverage."""
from __future__ import annotations


def evaluate_batch_coverage(total_candidates: int, tested: int, observed: int,
                            rejected: int, promoted: int, skipped: int = 0) -> dict:
    fields = (total_candidates, tested, observed, rejected, promoted, skipped)
    if any(type(x) is not int or x < 0 for x in fields):
        raise ValueError("INVALID_BATCH_COUNTS")
    if tested > total_candidates or observed + rejected + promoted != tested:
        raise ValueError("INCONSISTENT_BATCH_COUNTS")
    untested = total_candidates - tested
    return {
        "total_candidates": total_candidates,
        "tested": tested,
        "untested": untested,
        "skipped": skipped,
        "coverage_complete": untested == 0 and skipped == 0,
        "promotion_allowed": False,
        "walk_forward_required": True,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
