from dataclasses import dataclass
from typing import Literal


Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class SubsystemHealth:
    id: str
    name: str
    domain: str
    health_score: float  # 0.0 - 1.0
    severity: Severity
    description: str


@dataclass
class HealingAction:
    id: str
    target_subsystem_id: str
    title: str
    description: str
    automated_possible: bool
    playbook_ref: str


def health_to_dict(h: SubsystemHealth) -> dict:
    return {
        "id": h.id,
        "name": h.name,
        "domain": h.domain,
        "health_score": h.health_score,
        "severity": h.severity,
        "description": h.description,
    }


def action_to_dict(a: HealingAction) -> dict:
    return {
        "id": a.id,
        "target_subsystem_id": a.target_subsystem_id,
        "title": a.title,
        "description": a.description,
        "automated_possible": a.automated_possible,
        "playbook_ref": a.playbook_ref,
    }

