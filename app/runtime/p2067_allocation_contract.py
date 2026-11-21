"""Fail-closed P2067 allocation reconciliation. Research/PAPER only; no broker access."""
from decimal import Decimal, InvalidOperation


def reconcile_p2067_weights(rows, *, declared_reserve=None):
    if not isinstance(rows, list) or not rows:
        raise ValueError("P2067_EMPTY_ALLOCATION")
    seen = set()
    total = Decimal("0")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("P2067_INVALID_ALLOCATION")
        sid = row.get("specialist_id")
        if not isinstance(sid, str) or not sid.strip() or sid in seen:
            raise ValueError("P2067_INVALID_SPECIALIST")
        seen.add(sid)
        value = row.get("normalized_weight")
        if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
            raise ValueError("P2067_INVALID_WEIGHT")
        try:
            weight = Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError("P2067_INVALID_WEIGHT") from exc
        if not weight.is_finite() or weight < 0 or weight > 1:
            raise ValueError("P2067_INVALID_WEIGHT")
        total += weight
    if total > 1:
        raise ValueError("P2067_OVERALLOCATED")
    residual = Decimal("1") - total
    if declared_reserve is None:
        if residual != 0:
            raise ValueError("P2067_UNDECLARED_RESIDUAL")
    else:
        if isinstance(declared_reserve, bool) or not isinstance(declared_reserve, (int, float, str, Decimal)):
            raise ValueError("P2067_INVALID_RESERVE")
        try:
            reserve = Decimal(str(declared_reserve))
        except InvalidOperation as exc:
            raise ValueError("P2067_INVALID_RESERVE") from exc
        if not reserve.is_finite() or reserve < 0 or reserve != residual:
            raise ValueError("P2067_RESERVE_MISMATCH")
    return {"allocated": str(total), "reserve": str(residual), "specialists": len(seen)}
