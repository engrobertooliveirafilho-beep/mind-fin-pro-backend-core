"""Offline financial-certification boundary; never emits or authorizes signals."""
from app.runtime.et618_financial_validation import (
    CertificationBlocked, bootstrap, net_trades, profit_factor,
)

def validate_financial_evidence(rows, provenance, costs, *, seed=618):
    """Validate already reconciled monetary trade evidence, not a strategy approval."""
    if not isinstance(provenance, dict) or not isinstance(costs, dict):
        raise CertificationBlocked("missing provenance or costs")
    if provenance.get("source_verified") is not True or not provenance.get("sha256_verified") is True:
        raise CertificationBlocked("unverified original ledger")
    if provenance.get("mode") != "PAPER_ONLY" or provenance.get("real_orders") != "FORBIDDEN" or provenance.get("ftmo_real") != "FORBIDDEN":
        raise CertificationBlocked("unsafe provenance")
    if provenance.get("pnl_unit") != "account_currency" or provenance.get("cost_unit") != "account_currency":
        raise CertificationBlocked("price-point PnL cannot be combined with monetary costs")
    edge = provenance.get("edge_id")
    if not isinstance(edge, str) or not edge.strip():
        raise CertificationBlocked("unreconciled edge_id")
    if set(costs) != {"spread", "slippage", "commission"}:
        raise CertificationBlocked("missing explicit cost dimensions")
    if not rows or any(not isinstance(row, dict) for row in rows):
        raise CertificationBlocked("missing trade-level ledger")
    if any(row.get("pnl_unit") != "account_currency" for row in rows):
        raise CertificationBlocked("unverified trade pnl unit")
    net = net_trades(rows, costs["spread"], costs["slippage"], costs["commission"], expected_edge_id=edge)
    pf = profit_factor(net)
    simulations = bootstrap(net, seed=seed, simulations=1000)
    return {
        "status": "FINANCIAL_METRICS_VALIDATED_PAPER_ONLY",
        "strategy_approved": False,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "edge_id": edge,
        "trade_count": len(net),
        "net_profit_factor": str(pf),
        "mc_simulations": len(simulations),
        "mc_seed": seed,
    }
