import json
from pathlib import Path

from subprocess import run
import sys

def test_p475_registry_builds():
    result = run(
        [sys.executable, "tools/build_universal_capability_registry.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    registry = Path("app/runtime/universal_capability_registry.json")
    assert registry.exists()

    data = json.loads(registry.read_text(encoding="utf-8"))
    assert data["registry"] == "P4.75_UNIVERSAL_CAPABILITY_REGISTRY"
    assert "capabilities" in data
    assert "semantic_retrieval" in data["capabilities"]
    assert data["capabilities"]["semantic_retrieval"]["eligible_for_runtime"] is True
