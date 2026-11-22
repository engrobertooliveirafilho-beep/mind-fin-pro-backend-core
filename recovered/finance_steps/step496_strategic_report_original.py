from datetime import datetime, timezone
from typing import Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_product_metrics() -> Dict:
    return {
        "active_users": 1280,
        "retention_rate": 0.71,
        "feature_usage_top": ["mind-meeting", "financial-agent", "reports"],
        "new_signups_7d": 93,
    }


def _mock_financial_metrics() -> Dict:
    return {
        "mrr_usd": 14820,
        "growth_rate_30d": 0.12,
        "churn_rate": 0.04,
        "pipeline_value_usd": 52100,
    }


def _mock_agent_metrics() -> Dict:
    return {
        "avg_response_ms": 183,
        "error_rate": 0.02,
        "active_agents": 7,
        "tasks_last_24h": 312,
    }


def _mock_risk_indicators() -> List[Dict]:
    return [
        {"id": "llm-cost", "severity": "medium", "description": "Uso crescente de tokens."},
        {"id": "latency-spike", "severity": "low", "description": "Pequena oscilação de latência."},
    ]


def generate_strategic_report() -> Dict:
    return {
        "version": "step496-v1",
        "generated_at": _now(),
        "status": "ok",
        "product": _mock_product_metrics(),
        "financial": _mock_financial_metrics(),
        "agents": _mock_agent_metrics(),
        "risk": _mock_risk_indicators(),
    }

