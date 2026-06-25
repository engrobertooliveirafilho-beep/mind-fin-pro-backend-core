from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class UserCognitiveMirror:
    tone: str = "direct"
    detail_level: str = "adaptive"
    decision_style: str = "practical"
    vocabulary: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)
    recurring_goals: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    reasoning_pattern: str = "goal_first"
    confidence: float = 0.0


@dataclass
class ConversationReview:
    conversation_id_hash: str
    domain: str
    intent: str
    user_goal: str
    goal_completion_score: float
    continuity_score: float
    naturalness_score: float
    precision_score: float
    empathy_score: float
    mirror_alignment_score: float
    failure_types: List[str] = field(default_factory=list)
    root_causes: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    safe_summary_no_raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
