"""ET665.I negative regression: PAPER broker rejection must fail closed.

This test is intentionally NOT executed by the disabled CI workflow.
"""
from unittest.mock import patch

from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config


def test_paper_broker_rejection_cannot_be_reported_as_accepted(tmp_path):
    config = tmp_path / "ftmo.json"
    save_default_ftmo_config(str(config))
    gateway = ExecutionGateway(
        str(tmp_path / "execution.jsonl"),
        str(config),
        str(tmp_path / "session.json"),
        str(tmp_path / "day.jsonl"),
        str(tmp_path / "broker.jsonl"),
    )
    assert gateway.paper.open_session()["decision"] == "SESSION_OPENED"
    trade = {
        "symbol": "WIN", "side": "BUY", "strategy_id": "S1",
        "entry": 100, "stop": 98, "target": 104,
        "risk_amount": 500, "open_risk": 0, "daily_pnl": 0,
        "total_pnl": 0, "daily_trades": 1, "loss_streak": 0,
    }
    regime = {"regime": "TREND_UP", "normalized_atr": 0.005, "trade_allowed": True}
    genome = {"genome_id": "g1", "regime": "TREND_UP", "edge_claim": "NONE"}
    rejection = {
        "decision": "PAPER_ORDER_REJECTED_FILL",
        "fill": {"filled": False, "decision": "FILL_REJECT_INVALID_SIDE"},
        "production": "BLOCKED", "live": "FORBIDDEN",
    }
    with patch("mind_trader.app.execution.gateway.paper_route_order", return_value=rejection):
        result = gateway.submit_order("PAPER", trade, regime, genome)
    assert result["paper_broker"]["decision"] == "PAPER_ORDER_REJECTED_FILL"
    assert result["decision"] != "ACCEPT_SIMULATED_ORDER"
    assert result["order_status"] != "SIMULATED_ACCEPTED"
    assert result["production"] == "BLOCKED"
