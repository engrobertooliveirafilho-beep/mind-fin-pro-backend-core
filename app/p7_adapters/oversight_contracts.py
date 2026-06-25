from pydantic import BaseModel, Field
from typing import Any, Literal


OversightDecisionType = Literal["ALLOW", "REVIEW", "BLOCK", "REWRITE", "ESCALATE"]


class OversightInput(BaseModel):
    candidate_action: str
    reasoning_summary: str
    context: dict[str, Any] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)
    policy_constraints: list[str] = Field(default_factory=list)
    runtime_state: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None
    execution_mode: str = "shadow"


class OversightDecision(BaseModel):
    decision: OversightDecisionType
    allowed: bool
    reason: str
    risk_level: str
    required_revision: str | None = None
    audit_trace: list[str] = Field(default_factory=list)
