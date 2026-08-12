import json
from pathlib import Path

def test_p490_sovereign_certification():
    cert = json.loads(
        Path("runtime/certification/sovereign_technical_capacity_certification.json").read_text(encoding="utf-8")
    )

    assert cert["milestone"] == "P4.90 COMPLETE"
    assert cert["certification"] == "SOVEREIGN_TECHNICAL_CAPACITY_CERTIFICATION"
    assert cert["status"] == "CERTIFIED"
    assert cert["missing_required_artifacts"] == []

    required_scope = [
        "discovery",
        "registry",
        "recovery",
        "reconstruction",
        "prioritization",
        "governance",
        "knowledge_graph",
        "repository_intelligence",
        "file_ingestion",
        "multi_extension_reader",
        "knowledge_extraction",
        "safe_routing",
    ]

    for key in required_scope:
        assert cert["scope"][key].startswith("CERTIFIED")

    assert cert["governance"]["physical_delete"] == "FORBIDDEN"
    assert cert["governance"]["unsafe_auto_execution"] == "FORBIDDEN"
    assert cert["governance"]["p483_gate"] == "ENFORCED"
    assert cert["metrics"]["files_checked"] >= 1
    assert cert["metrics"]["knowledge_items"] >= 1
