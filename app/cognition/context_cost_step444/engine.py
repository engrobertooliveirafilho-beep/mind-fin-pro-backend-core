from datetime import datetime, timezone
from typing import List, Dict, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

Strategy = Literal["priority_first", "cheap_first"]


class ContextSegment(BaseModel):
    segment_id: str = Field(..., min_length=1, max_length=128)
    tokens: int = Field(..., gt=0, le=100000000)
    priority: int = Field(..., ge=1, le=10)
    cost_per_1k: float = Field(..., gt=0.0, le=1000000, allow_inf_nan=False)


class BalanceRequest(BaseModel):
    segments: List[ContextSegment] = Field(..., max_length=10000)
    max_tokens: int = Field(..., gt=0, le=100000000)
    max_cost: float = Field(..., gt=0.0, le=1000000, allow_inf_nan=False)
    strategy: Strategy = "priority_first"


class ContextAllocation(BaseModel):
    segment_id: str
    included_tokens: int
    estimated_cost: float
    status: Literal["included", "partial", "dropped"]
    reason: str


class BalanceResponse(BaseModel):
    allocations: List[ContextAllocation]
    totals: Dict[str, Any]
    meta: Dict[str, Any]


def _sort_segments(segments: List[ContextSegment], strategy: Strategy) -> List[ContextSegment]:
    if strategy == "cheap_first":
        # mais barato primeiro, desempate por maior prioridade
        return sorted(segments, key=lambda s: (s.cost_per_1k, -s.priority))
    # default: prioridade alta primeiro, desempate por menor custo
    return sorted(segments, key=lambda s: (-s.priority, s.cost_per_1k))


def _estimate_cost(tokens: int, cost_per_1k: float) -> float:
    return (tokens / 1000.0) * cost_per_1k


@router.post("/balance", response_model=BalanceResponse)
def balance_context(request: BalanceRequest) -> BalanceResponse:
    if len({s.segment_id for s in request.segments}) != len(request.segments):
        raise HTTPException(status_code=422, detail='duplicate segment_id')
    remaining_tokens = request.max_tokens
    remaining_cost = request.max_cost

    allocations: List[ContextAllocation] = []
    sorted_segments = _sort_segments(request.segments, request.strategy)

    for seg in sorted_segments:
        if remaining_tokens <= 0 or remaining_cost <= 0:
            allocations.append(
                ContextAllocation(
                    segment_id=seg.segment_id,
                    included_tokens=0,
                    estimated_cost=0.0,
                    status="dropped",
                    reason="no_budget_left",
                )
            )
            continue

        full_cost = _estimate_cost(seg.tokens, seg.cost_per_1k)

        # cabe tudo
        if seg.tokens <= remaining_tokens and full_cost <= remaining_cost:
            remaining_tokens -= seg.tokens
            remaining_cost -= full_cost
            allocations.append(
                ContextAllocation(
                    segment_id=seg.segment_id,
                    included_tokens=seg.tokens,
                    estimated_cost=round(full_cost, 6),
                    status="included",
                    reason="full_fit",
                )
            )
            continue

        # tenta parcial
        max_tokens_by_budget = int((remaining_cost / seg.cost_per_1k) * 1000.0)
        # Guard against floating-point rounding allocating beyond remaining budget.
        while max_tokens_by_budget > 0 and _estimate_cost(max_tokens_by_budget, seg.cost_per_1k) > remaining_cost:
            max_tokens_by_budget -= 1
        partial_tokens = min(remaining_tokens, max_tokens_by_budget)

        if partial_tokens > 0:
            cost_partial = _estimate_cost(partial_tokens, seg.cost_per_1k)
            remaining_tokens -= partial_tokens
            remaining_cost -= cost_partial
            allocations.append(
                ContextAllocation(
                    segment_id=seg.segment_id,
                    included_tokens=partial_tokens,
                    estimated_cost=round(cost_partial, 6),
                    status="partial",
                    reason="partial_fit",
                )
            )
        else:
            allocations.append(
                ContextAllocation(
                    segment_id=seg.segment_id,
                    included_tokens=0,
                    estimated_cost=0.0,
                    status="dropped",
                    reason="insufficient_budget",
                )
            )

    total_tokens = sum(a.included_tokens for a in allocations)
    total_cost = sum(a.estimated_cost for a in allocations)

    totals = {
        "requested_segments": len(request.segments),
        "allocated_segments": sum(1 for a in allocations if a.included_tokens > 0),
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6),
        "max_tokens": request.max_tokens,
        "max_cost": request.max_cost,
        "strategy": request.strategy,
    }

    return BalanceResponse(
        allocations=allocations,
        totals=totals,
        meta={
            "version": "step444-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "engine": "context_cost_balancer_step444",
        },
    )

