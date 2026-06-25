from pydantic import BaseModel, Field
from typing import Any, Optional


class HierarchyNode(BaseModel):
    node_id: str
    parent_id: Optional[str] = None
    title: str
    objective: str
    status: str = "planned"
    dependencies: list[str] = Field(default_factory=list)
    children: list["HierarchyNode"] = Field(default_factory=list)
    suggested_tool: Optional[str] = None


class HierarchicalPlanRequest(BaseModel):
    user_intent: str
    goal: str
    context: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    available_tools: list[str] = Field(default_factory=list)
    continuity_state: dict[str, Any] = Field(default_factory=dict)
    max_depth: int = 3


class HierarchicalPlanResponse(BaseModel):
    root_goal: str
    nodes: list[HierarchyNode]
    execution_order: list[str]
    tool_requirements: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    next_action: str
