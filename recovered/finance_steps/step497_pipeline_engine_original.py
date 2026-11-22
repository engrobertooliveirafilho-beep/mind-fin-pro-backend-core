from datetime import datetime, timezone
from typing import Dict, List


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_stages() -> List[Dict]:
    return [
        {
            "id": "cold-leads",
            "name": "Leads frios",
            "leads_count": 120,
            "conversion_prob": 0.05,
        },
        {
            "id": "qualified",
            "name": "Oportunidades qualificadas",
            "leads_count": 32,
            "conversion_prob": 0.35,
        },
        {
            "id": "proposal",
            "name": "Propostas enviadas",
            "leads_count": 9,
            "conversion_prob": 0.6,
        },
        {
            "id": "closed-won",
            "name": "Fechados (ganhos)",
            "leads_count": 4,
            "conversion_prob": 1.0,
        },
    ]


def _mock_next_actions() -> List[Dict]:
    return [
        {
            "id": "followup-proposals",
            "stage": "proposal",
            "title": "Follow-up nas propostas abertas",
            "priority": "high",
        },
        {
            "id": "nurture-cold",
            "stage": "cold-leads",
            "title": "Rodar campanha de nutrição para leads frios",
            "priority": "medium",
        },
        {
            "id": "deep-dive-qualified",
            "stage": "qualified",
            "title": "Reuniões de diagnóstico com oportunidades qualificadas",
            "priority": "high",
        },
    ]


def _mock_metrics() -> Dict:
    return {
        "estimated_monthly_recurring_revenue_usd": 18000,
        "estimated_pipeline_value_usd": 60000,
        "avg_cycle_days": 21,
    }


def get_business_pipeline_snapshot() -> Dict:
    return {
        "version": "step497-v1",
        "generated_at": _now_utc_iso(),
        "status": "ok",
        "stages": _mock_stages(),
        "next_actions": _mock_next_actions(),
        "metrics": _mock_metrics(),
    }

