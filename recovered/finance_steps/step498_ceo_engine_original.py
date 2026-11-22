from datetime import datetime, timezone
from typing import Dict

from app.modules.strategic_report.report_engine import generate_strategic_report
from app.modules.business_pipeline.pipeline_engine import get_business_pipeline_snapshot
from app.modules.self_optimization.opt_engine import get_self_optimization_snapshot
from app.modules.self_healing.healing_engine import get_self_healing_snapshot


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_ceo_briefing() -> Dict:
    strategic = generate_strategic_report()
    pipeline = get_business_pipeline_snapshot()
    self_opt = get_self_optimization_snapshot()
    self_heal = get_self_healing_snapshot()

    return {
        "version": "step498-v1",
        "generated_at": _now_utc_iso(),
        "status": "ok",
        "strategic": strategic,
        "pipeline": pipeline,
        "self_optimization": self_opt,
        "self_healing": self_heal,
    }

