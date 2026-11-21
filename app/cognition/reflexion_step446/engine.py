from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ReflexionIteration(BaseModel):
    round: int
    raw_thought: str
    critique: str
    improved_thought: str


class ReflexionRequest(BaseModel):
    topic: str
    initial_thought: str
    max_rounds: int = Field(3, ge=1, le=8)


class ReflexionResponse(BaseModel):
    topic: str
    iterations: List[ReflexionIteration]
    final_summary: str
    meta: Dict[str, Any]


def _generate_critique(thought: str, round_id: int) -> str:
    base = thought.strip()
    if len(base) < 40:
        return f"r{round_id}: pensamento curto, adicionar mais detalhes e implicacoes praticas."
    if "risco" not in base.lower():
        return f"r{round_id}: falta considerar riscos e trade-offs."
    return f"r{round_id}: pensamento razoavel, pode sintetizar melhor os pontos chave."


def _improve_thought(thought: str, critique: str, round_id: int) -> str:
    return f"[r{round_id}-improved] {thought.strip()} | REFLEXAO: {critique}"


@router.post("/run", response_model=ReflexionResponse)
def run_reflexion_loop(request: ReflexionRequest) -> ReflexionResponse:
    iterations: List[ReflexionIteration] = []
    current_thought = request.initial_thought.strip()
    rounds = max(1, min(request.max_rounds, 8))

    for r in range(1, rounds + 1):
        critique = _generate_critique(current_thought, r)
        improved = _improve_thought(current_thought, critique, r)
        iterations.append(
            ReflexionIteration(
                round=r,
                raw_thought=current_thought,
                critique=critique,
                improved_thought=improved,
            )
        )
        current_thought = improved

    final_summary = (
        f"Loop de reflexao sobre '{request.topic}' com {rounds} iteracoes; "
        f"pensamento final incorpora autocritica progressiva."
    )

    return ReflexionResponse(
        topic=request.topic,
        iterations=iterations,
        final_summary=final_summary,
        meta={
            "version": "step446-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "reflexion_loop_step446",
            "rounds": rounds,
        },
    )

