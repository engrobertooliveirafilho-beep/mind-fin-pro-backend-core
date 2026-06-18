from .core import P55AOrchestrator
from .engines import *

def run_healthcheck() -> dict:
    o = P55AOrchestrator()
    return {
        "status": "P5.5A_READY",
        "mission": o.mission,
        "modules_count": len(o.manifest()["modules"]),
        "agents_count": len(o.manifest()["agents"]),
        "executive_questions_count": len(o.executive_question_types())
    }
