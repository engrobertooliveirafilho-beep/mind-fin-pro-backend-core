from __future__ import annotations

from pydantic import BaseModel
from typing import List, Literal


class AgentStep(BaseModel):
    tool: Literal["calc", "fetch", "talk"]
    input: str


class AgentPlan(BaseModel):
    steps: List[AgentStep]
    summary: str


class AgentRequest(BaseModel):
    session_id: str
    goal: str
