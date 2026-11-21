from datetime import datetime, timezone
from typing import List, Dict, Any, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

TagType = Literal["risk", "opportunity", "execution", "finance", "other"]


class StrategicPoint(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    tag: TagType = "other"
    weight: float = Field(0.5, ge=0.0, le=1.0)


class SummaryRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=4096)
    points: List[StrategicPoint] = Field(..., max_length=2048)
    max_items: int = Field(5, ge=1, le=20)
    focus_tags: Optional[List[TagType]] = Field(None, max_length=5)


class SummaryItem(BaseModel):
    text: str
    tag: TagType
    weight: float
    normalized_weight: float
    included: bool
    reason: str


class SummaryResponse(BaseModel):
    topic: str
    items: List[SummaryItem]
    stats: Dict[str, Any]
    meta: Dict[str, Any]


def _filter_points(points: List[StrategicPoint], focus_tags: Optional[List[TagType]]) -> List[StrategicPoint]:
    if not focus_tags:
        return points
    tags_set = set(focus_tags)
    return [p for p in points if p.tag in tags_set]


def _normalize_weights(points: List[StrategicPoint]) -> Dict[str, float]:
    total = sum(p.weight for p in points) or 1.0
    return {str(id(p)): p.weight / total for p in points}


@router.post("/run", response_model=SummaryResponse)
def run_strategic_summary(request: SummaryRequest) -> SummaryResponse:
    if not request.points:
        return SummaryResponse(
            topic=request.topic,
            items=[],
            stats={
                "points_received": 0,
                "points_considered": 0,
                "max_items": request.max_items,
            },
            meta={
                "version": "step448-v1",
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "engine": "strategic_summary_step448",
            },
        )

    filtered = _filter_points(request.points, request.focus_tags)
    # Empty focus matches stay empty; never silently ignore the user's filter.

    normalized_map = _normalize_weights(filtered)
    sorted_points = sorted(enumerate(filtered), key=lambda pair: pair[1].weight, reverse=True)

    selected_indices = {idx for idx, _ in sorted_points[: request.max_items]}
    items: List[SummaryItem] = []

    for idx, p in sorted_points:
        included = idx in selected_indices
        reason = "selected_by_weight"
        if not included:
            reason = "dropped_low_priority"

        items.append(
            SummaryItem(
                text=p.text,
                tag=p.tag,
                weight=p.weight,
                normalized_weight=round(normalized_map[str(id(p))], 4),
                included=included,
                reason=reason,
            )
        )

    stats = {
        "points_received": len(request.points),
        "points_considered": len(filtered),
        "max_items": request.max_items,
        "items_included": sum(1 for i in items if i.included),
        "focus_tags": request.focus_tags or [],
    }

    return SummaryResponse(
        topic=request.topic,
        items=items,
        stats=stats,
        meta={
            "version": "step448-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "engine": "strategic_summary_step448",
        },
    )

