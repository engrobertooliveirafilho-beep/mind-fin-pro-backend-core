"""ET665.MB.R9: adversarial validation rejects malformed review context."""
import pytest
from mind_trader.app.validation.adversarial_ai import AdversarialValidationEngine

@pytest.mark.parametrize("which,value", [
    ("trade", None), ("trade", []), ("trade", {"risk_amount": True}),
    ("trade", {"risk_amount": float("nan")}), ("trade", {"entry": "100"}),
    ("trade", {"stop": float("inf")}), ("regime", None),
    ("regime", {"normalized_atr": float("nan")}), ("genome", []),
    ("genome", {"risk_amount": float("-inf")}),
])
def test_malformed_or_nonfinite_context_vetoes_trade(which, value):
    trade={"risk_amount": 10.0, "entry": 100.0, "stop": 98.0, "target": 104.0,
           "loss_streak": 0, "daily_trades": 0, "open_risk": 0.0,
           "daily_pnl": 0.0, "total_pnl": 0.0}
    regime={"regime": "TRENDING", "normalized_atr": 0.01}
    genome={"genome_id": "SYNTHETIC", "regime": "TRENDING", "edge_claim": "NONE"}
    if which == "trade":
        trade=value
    elif which == "regime":
        regime=value
    else:
        genome=value
    result=AdversarialValidationEngine().review_trade(trade, regime, genome)
    assert result["adversarial_passed"] is False
    assert result["decision"] == "VETO_TRADE"
    assert result["production"] == "BLOCKED"

@pytest.mark.parametrize("field,value", [
    ("target", -1e308),
    ("open_risk", 1e308),
    ("risk_amount", 1e308),
])
def test_finite_inputs_with_overflowing_intermediates_are_vetoed(field, value):
    trade={"risk_amount": 10.0, "entry": 1e308, "stop": -1e308, "target": 1e308,
           "open_risk": 0.0, "daily_pnl": 0.0, "total_pnl": 0.0}
    trade[field]=value
    regime={"regime":"TRENDING","normalized_atr":0.01}
    genome={"genome_id":"SYNTHETIC","regime":"TRENDING","edge_claim":"NONE"}
    result=AdversarialValidationEngine().review_trade(trade,regime,genome)
    assert result["adversarial_passed"] is False
    assert result["decision"]=="VETO_TRADE"
    assert all(review["passed"] is False for review in result["reviews"])
