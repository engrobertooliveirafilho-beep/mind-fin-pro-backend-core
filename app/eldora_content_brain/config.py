from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrainSettings:
    repo_root: Path
    runtime_root: Path
    output_root: Path
    market: str
    locale: str
    research_model: str
    image_model: str
    max_decisions: int
    minimum_confidence: float
    source_domains: list[str]
    guardrails: list[str]

    @classmethod
    def load(cls, path: Path) -> "BrainSettings":
        data = json.loads(path.read_text(encoding="utf-8"))
        repo_root = Path(__file__).resolve().parents[2]
        return cls(
            repo_root=repo_root,
            runtime_root=repo_root / data["runtime_root"],
            output_root=repo_root / data["output_root"],
            market=data["market"],
            locale=data["locale"],
            research_model=data["research_model"],
            image_model=data["image_model"],
            max_decisions=int(data["max_decisions"]),
            minimum_confidence=float(data["minimum_confidence"]),
            source_domains=list(data["source_domains"]),
            guardrails=list(data["guardrails"]),
        )