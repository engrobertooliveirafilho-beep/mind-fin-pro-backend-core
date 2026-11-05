"""ET618: isolated PAPER_ONLY trade-level financial validator. No signal emission."""
from decimal import Decimal, InvalidOperation
from random import Random

class CertificationBlocked(ValueError):
    pass

def dec(value):
    if isinstance(value, (float, bool)):
        raise CertificationBlocked("float/bool forbidden")
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CertificationBlocked("invalid decimal") from exc
    if not x.is_finite():
        raise CertificationBlocked("nonfinite decimal")
    return x

def profit_factor(trades):
    values = [dec(x) for x in trades]
    if not values:
        raise CertificationBlocked("empty ledger")
    gains = sum((x for x in values if x > 0), Decimal(0))
    losses = -sum((x for x in values if x < 0), Decimal(0))
    if not losses:
        raise CertificationBlocked("zero gross losses; PF undefined")
    return gains / losses

def net_trades(ledger, spread, slippage, commission, *, expected_edge_id):
    if not ledger:
        raise CertificationBlocked("missing trade-level ledger")
    costs = [dec(spread), dec(slippage), dec(commission)]
    if any(x < 0 for x in costs):
        raise CertificationBlocked("negative cost")
    seen = set()
    out = []
    for row in ledger:
        if row.get("edge_id") != expected_edge_id or not row.get("trade_id"):
            raise CertificationBlocked("missing or mismatched edge/trade identity")
        if row["trade_id"] in seen:
            raise CertificationBlocked("duplicate trade_id")
        seen.add(row["trade_id"])
        if row.get("mode") != "PAPER_ONLY" or row.get("real_orders") != "FORBIDDEN":
            raise CertificationBlocked("unsafe trade mode")
        out.append(dec(row["pnl"]) - sum(costs))
    return out

def bootstrap(trades, *, seed, simulations=1000):
    values = [dec(x) for x in trades]
    if not values:
        raise CertificationBlocked("empty ledger")
    if not isinstance(seed, int) or isinstance(seed, bool) or not isinstance(simulations, int) or simulations < 1:
        raise CertificationBlocked("invalid simulation configuration")
    rng = Random(seed)
    outcomes = []
    for _ in range(simulations):
        sample = [values[rng.randrange(len(values))] for _ in values]
        total = sum(sample, Decimal(0))
        peak = equity = dd = Decimal(0)
        for pnl in sample:
            equity += pnl
            peak = max(peak, equity)
            dd = max(dd, peak - equity)
        try:
            pf = profit_factor(sample)
        except CertificationBlocked:
            pf = None
        outcomes.append({"net_pnl": total, "max_drawdown": dd, "pf": pf})
    return outcomes
