from decimal import Decimal
import pytest
from app.runtime.et618_financial_validation import CertificationBlocked, bootstrap, dec, net_trades, profit_factor

def trade(i, pnl, edge="E"):
    return {"trade_id": str(i), "edge_id": edge, "pnl": pnl, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN"}

def test_pf_exact():
    assert profit_factor(["3", "-2"]) == Decimal("1.5")

def test_pf_no_losses_blocks():
    with pytest.raises(CertificationBlocked):
        profit_factor(["3", "2"])

def test_decimal_comma_not_silently_accepted():
    with pytest.raises(CertificationBlocked):
        dec("1,5838")

def test_float_blocks():
    with pytest.raises(CertificationBlocked):
        dec(1.5)

def test_net_costs_each_trade():
    assert net_trades([trade(1, "5"), trade(2, "-2")], "0.5", "0.25", "0.25", expected_edge_id="E") == [Decimal("4.00"), Decimal("-3.00")]

def test_duplicate_blocks():
    with pytest.raises(CertificationBlocked):
        net_trades([trade(1, "1"), trade(1, "-1")], "0", "0", "0", expected_edge_id="E")

def test_wrong_edge_blocks():
    with pytest.raises(CertificationBlocked):
        net_trades([trade(1, "1", "OTHER")], "0", "0", "0", expected_edge_id="E")

def test_unsafe_mode_blocks():
    row = trade(1, "1")
    row["real_orders"] = "ALLOWED"
    with pytest.raises(CertificationBlocked):
        net_trades([row], "0", "0", "0", expected_edge_id="E")

def test_missing_ledger_blocks():
    with pytest.raises(CertificationBlocked):
        net_trades([], "0", "0", "0", expected_edge_id="E")

def test_negative_cost_blocks():
    with pytest.raises(CertificationBlocked):
        net_trades([trade(1, "1")], "-1", "0", "0", expected_edge_id="E")

def test_monte_carlo_reproducible():
    a = bootstrap(["4", "-2", "1"], seed=618, simulations=30)
    assert a == bootstrap(["4", "-2", "1"], seed=618, simulations=30)

def test_monte_carlo_empty_blocks():
    with pytest.raises(CertificationBlocked):
        bootstrap([], seed=618)

def test_monte_carlo_boolean_seed_blocks():
    with pytest.raises(CertificationBlocked):
        bootstrap(["1", "-1"], seed=True)

def test_stress_can_reduce_pf():
    rows = [trade(1, "4"), trade(2, "-2")]
    base = profit_factor([r["pnl"] for r in rows])
    net = profit_factor(net_trades(rows, "0.5", "0.25", "0.25", expected_edge_id="E"))
    assert net < base
