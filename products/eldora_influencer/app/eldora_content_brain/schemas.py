from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrendEvidence:
    source_title: str
    source_url: str
    observation: str
    relevance: float
    freshness: str
    category: str


@dataclass
class CreativeDecision:
    content_id: str
    objective: str
    platform: str
    format: str
    scene: str
    wardrobe: str
    hair: str
    makeup: str
    prop: str
    text_element: str
    caption_angle: str
    cta: str
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "PLANNED"


@dataclass
class ResearchPlan:
    schema: str
    run_id: str
    researched_at_utc: str
    market: str
    persona: str
    evidence: list[dict[str, Any]]
    decisions: list[dict[str, Any]]
    rejected_trends: list[dict[str, Any]]
    guardrails: list[str]