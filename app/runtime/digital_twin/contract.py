from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class TwinSignal:
    name: str
    value: str
    confidence: float
    evidence_count: int = 0


@dataclass
class CognitiveDigitalTwin:
    user_id_hash: str
    behavior_model: List[TwinSignal] = field(default_factory=list)
    communication_model: List[TwinSignal] = field(default_factory=list)
    decision_model: List[TwinSignal] = field(default_factory=list)
    learning_model: List[TwinSignal] = field(default_factory=list)
    goal_model: List[TwinSignal] = field(default_factory=list)
    emotional_model: List[TwinSignal] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def confidence_gate(signals: List[TwinSignal], threshold: float = 0.70) -> List[TwinSignal]:
    return [s for s in signals if s.confidence >= threshold]


def twin_to_instruction(twin: CognitiveDigitalTwin, threshold: float = 0.70) -> str:
    groups = {
        "behavior": confidence_gate(twin.behavior_model, threshold),
        "communication": confidence_gate(twin.communication_model, threshold),
        "decision": confidence_gate(twin.decision_model, threshold),
        "learning": confidence_gate(twin.learning_model, threshold),
        "goals": confidence_gate(twin.goal_model, threshold),
        "emotional": confidence_gate(twin.emotional_model, threshold),
    }

    lines = [
        "Adapte a resposta ao modelo cognitivo do usuário.",
        "Não imite literalmente. Organize melhor o pensamento dele.",
        "Use apenas sinais com confiança suficiente.",
    ]

    for group, signals in groups.items():
        if signals:
            lines.append(f"{group}: " + "; ".join(f"{s.name}={s.value}" for s in signals))

    return "\n".join(lines)
