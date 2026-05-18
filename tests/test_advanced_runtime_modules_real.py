import importlib
from pathlib import Path

def test_advanced_runtime_modules_are_real():
    expected = [
        p for p in Path("app/runtime").glob("*.py")
        if p.name not in {"__init__.py"} and not p.name.startswith("__")
    ]
    assert expected
    for p in expected:
        m = importlib.import_module("app.runtime."+p.stem)
        if p.stem == "advanced_runtime_base":
            continue
        assert hasattr(m, "health")
        assert hasattr(m, "run")
        h=m.health()
        r=m.run({"text":"corrige bug com contexto e continuidade"})
        assert h["status"] == "operational"
        assert h.get("advanced") is True
        assert r["status"] == "operational"
        assert r["confidence"] >= 0.75
        assert r["trace_id"]
        assert r["signals"]
        assert r["actions"]
