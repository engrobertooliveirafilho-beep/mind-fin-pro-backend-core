from pathlib import Path
import os

def load_env():
    p = Path(".env")
    if p.exists():
        for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.runtime.capability_orchestrator import capability_orchestrator


def test_p474b_orchestrator_diagnostic_sections():
    out = capability_orchestrator("whatsapp:+5519996166906", "Roberto matemática", mode="diagnostic")
    assert out["orchestrator"] == "P4.74B_ORCHESTRATOR_DIAGNOSTIC_MODE"
    assert out["mode"] == "diagnostic"
    assert isinstance(out["capabilities_available"], list)
    assert isinstance(out["capabilities_used"], list)
    assert "retrieval" in out
    assert "social" in out
    assert "semantic_whatsapp" in out


def test_p474b_orchestrator_uses_retrieval_and_social():
    out = capability_orchestrator("whatsapp:+5519996166906", "qual é meu nome?", mode="diagnostic")
    assert "semantic_retrieval" in out["capabilities_used"]
    assert "social_memory" in out["capabilities_used"]
