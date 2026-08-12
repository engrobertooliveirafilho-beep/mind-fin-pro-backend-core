from pathlib import Path

from app.eldora_content_brain.config import BrainSettings
from app.eldora_content_brain.planner import normalize_plan


def settings(tmp_path: Path) -> BrainSettings:
    return BrainSettings(
        repo_root=tmp_path,
        runtime_root=tmp_path / "runtime",
        output_root=tmp_path / "output",
        market="Brasil",
        locale="pt-BR",
        research_model="gpt-5",
        image_model="gpt-image-1.5",
        max_decisions=5,
        minimum_confidence=0.70,
        source_domains=[],
        guardrails=["preservar identidade"],
    )


def test_rejects_decision_without_valid_evidence(tmp_path: Path) -> None:
    payload = {
        "evidence": [{"source_url": "https://fonte.test"}],
        "decisions": [{
            "content_id": "A",
            "confidence": 0.9,
            "evidence_refs": ["https://outra.test"],
        }],
        "rejected_trends": [],
    }
    result = normalize_plan(payload, settings(tmp_path))
    assert result["decisions"] == []
    assert result["rejected_trends"]


def test_accepts_grounded_decision(tmp_path: Path) -> None:
    payload = {
        "evidence": [{"source_url": "https://fonte.test"}],
        "decisions": [{
            "content_id": "A",
            "confidence": 0.9,
            "evidence_refs": ["https://fonte.test"],
        }],
        "rejected_trends": [],
    }
    result = normalize_plan(payload, settings(tmp_path))
    assert len(result["decisions"]) == 1