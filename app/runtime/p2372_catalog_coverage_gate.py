"""P2372 research-only coverage reconciliation; never synthesize M2 or promote edges."""
from __future__ import annotations


def reconcile_catalog_coverage(catalog: list[dict], backtested: list[dict]) -> dict:
    """Compare strategy identity without treating missing datasets as tested."""
    fields = ("family", "variant", "profile", "timeframe")
    def identity(row):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip() for k in fields):
            raise ValueError("INVALID_CATALOG_ROW")
        return tuple(row[k].strip() for k in fields)

    if not isinstance(catalog, list) or not isinstance(backtested, list):
        raise ValueError("INVALID_CATALOG_ENVELOPE")
    catalog_keys = [identity(x) for x in catalog]
    tested_keys = [identity(x) for x in backtested]
    if len(catalog_keys) != len(set(catalog_keys)) or len(tested_keys) != len(set(tested_keys)):
        raise ValueError("DUPLICATE_STRATEGY_KEY")
    if not set(tested_keys).issubset(set(catalog_keys)):
        raise ValueError("TESTED_STRATEGY_NOT_IN_CATALOG")
    missing = sorted(set(catalog_keys) - set(tested_keys))
    counts = {}
    for key in missing:
        counts[key[3]] = counts.get(key[3], 0) + 1
    return {
        "cataloged": len(catalog_keys),
        "backtested": len(tested_keys),
        "not_backtested": len(missing),
        "not_backtested_by_timeframe": counts,
        "coverage_complete": not missing,
        "promotion_allowed": False,
        "synthetic_m2_allowed": False,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
