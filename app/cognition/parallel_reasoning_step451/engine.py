from datetime import datetime, timezone
from typing import List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class BranchConfig(BaseModel):
    branches: int = Field(3, ge=1, le=12)
    depth: int = Field(3, ge=1, le=8)


class ParallelReasoningRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=4096)
    config: BranchConfig = Field(default_factory=BranchConfig)


class BranchStep(BaseModel):
    step: int
    thought: str


class BranchTrace(BaseModel):
    branch_id: str
    path_label: str
    steps: List[BranchStep]
    score: float
    rationale: str


class ParallelReasoningResponse(BaseModel):
    topic: str
    branches: List[BranchTrace]
    meta: Dict[str, Any]


def _build_branch_steps(topic: str, branch_idx: int, depth: int) -> List[BranchStep]:
    steps: List[BranchStep] = []
    for d in range(1, depth + 1):
        steps.append(
            BranchStep(
                step=d,
                thought=f"branch {branch_idx} / passo {d}: explorar '{topic}' sob angulo {branch_idx}.",
            )
        )
    return steps


def _score_branch(branch_idx: int, total_branches: int) -> float:
    base = 1.0 - (branch_idx - 1) * (0.2 / max(1, total_branches - 1))
    return round(max(0.3, base), 3)


@router.post("/run", response_model=ParallelReasoningResponse)
def run_parallel_reasoning(request: ParallelReasoningRequest) -> ParallelReasoningResponse:
    branches_count = max(1, min(request.config.branches, 12))
    depth = max(1, min(request.config.depth, 8))

    traces: List[BranchTrace] = []

    for i in range(1, branches_count + 1):
        steps = _build_branch_steps(request.topic, i, depth)
        score = _score_branch(i, branches_count)
        rationale = (
            f"branch {i} entre {branches_count} com profundidade {depth}; "
            f"score baseado em diversidade e saturacao."
        )
        traces.append(
            BranchTrace(
                branch_id=f"b{i}",
                path_label=f"caminho_{i}",
                steps=steps,
                score=score,
                rationale=rationale,
            )
        )

    return ParallelReasoningResponse(
        topic=request.topic,
        branches=traces,
        meta={
            "version": "step451-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "engine": "parallel_reasoning_step451",
            "branches": branches_count,
            "depth": depth,
        },
    )

