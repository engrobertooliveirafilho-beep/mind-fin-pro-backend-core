from app.runtime.p2091_2100_realtime_intelligence_layer import (
    PortfolioIntelligence, BehaviorAnalysis
)

def test_portfolio_intelligence_rejects_negative_pnl():
    specialists = [{"id":"A"},{"id":"B"},{"id":"C"}]
    p2081 = {"governance_metrics":{
        "equity":99000,"runtime_cycles":1500,
        "drawdown_pct":-0.01,"paper_mark_to_market_pnl":-1000
    }}
    result = PortfolioIntelligence().evaluate(specialists,p2081)
    assert result.status == "FAIL"
    assert result.payload["profitability_gate"] == "FAIL"

def test_overactive_behavior_is_not_accepted():
    result = BehaviorAnalysis().evaluate({"metrics":{
        "frames_built":100,"signals_generated":501,
        "open_positions":1,"closed_trades":10
    }})
    assert result.status == "FAIL"
    assert result.payload["behavior"] == "OVERACTIVE"

def test_overexposed_behavior_is_rejected():
    result = BehaviorAnalysis().evaluate({"metrics":{
        "frames_built":100,"signals_generated":10,
        "open_positions":4,"closed_trades":10
    }})
    assert result.status == "FAIL"
    assert result.payload["behavior"] == "OVEREXPOSED"
