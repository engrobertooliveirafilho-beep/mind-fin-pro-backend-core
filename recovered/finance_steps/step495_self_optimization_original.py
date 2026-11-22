from datetime import datetime, timezone
from typing import Dict, List


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_feature_usage() -> List[Dict]:
    # Tudo simulado, sem olhar para dados reais
    return [
        {
            "feature": "mind-meeting-webrtc",
            "calls_last_24h": 37,
            "avg_duration_seconds": 842,
            "error_rate": 0.01,
            "avg_latency_ms": 190,
        },
        {
            "feature": "financial-advisor-agent",
            "calls_last_24h": 112,
            "avg_duration_seconds": 120,
            "error_rate": 0.03,
            "avg_latency_ms": 260,
        },
        {
            "feature": "report-generator",
            "calls_last_24h": 18,
            "avg_duration_seconds": 45,
            "error_rate": 0.00,
            "avg_latency_ms": 140,
        },
    ]


def _mock_cost_signals() -> List[Dict]:
    return [
        {
            "id": "llm-usage-core",
            "service": "llm-provider-core",
            "estimated_daily_cost_usd": 42.5,
            "value_score": 0.8,
        },
        {
            "id": "vision-usage",
            "service": "vision-provider",
            "estimated_daily_cost_usd": 9.3,
            "value_score": 0.9,
        },
    ]


def _mock_optimization_suggestions() -> List[Dict]:
    return [
        {
            "id": "opt-high-latency-agents",
            "target": "financial-advisor-agent",
            "title": "Rever prompts e timeouts do agente financeiro",
            "category": "latency",
            "priority": "high",
        },
        {
            "id": "opt-llm-cost-window",
            "target": "llm-usage-core",
            "title": "Avaliar janelas de contexto e compressão",
            "category": "cost",
            "priority": "medium",
        },
    ]


def get_self_optimization_snapshot() -> Dict:
    feature_usage = _mock_feature_usage()
    cost_signals = _mock_cost_signals()
    suggestions = _mock_optimization_suggestions()

    return {
        "version": "step495-v1",
        "generated_at": _now_utc_iso(),
        "status": "ok",
        "feature_usage": feature_usage,
        "cost_signals": cost_signals,
        "suggestions": suggestions,
    }

