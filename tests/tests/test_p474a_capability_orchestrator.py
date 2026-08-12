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


def test_p474a_orchestrator_returns_core_sections():
    out = capability_orchestrator("whatsapp:+5519996166906", "Roberto matemática")
    assert out["orchestrator"] in [
        "P4.74A_CAPABILITY_ORCHESTRATOR",
        "P4.74B_ORCHESTRATOR_DIAGNOSTIC_MODE",
    ]
    assert "retrieval" in out
    assert "social" in out
    assert "semantic_whatsapp" in out


def test_p474a_orchestrator_retrieval_runs():
    out = capability_orchestrator("whatsapp:+5519996166906", "qual é meu nome?")
    assert out["retrieval"] is not None
    assert out["retrieval"]["rows"] >= 1

