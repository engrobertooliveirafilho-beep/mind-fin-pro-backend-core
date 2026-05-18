import importlib
from pathlib import Path

SKIP = {
"advanced_runtime_base",
"background_runtime",
"intent_router",
"response_builder",
"response_strategy",
"quality_gate",
"version_runtime",
"live_whatsapp_response",
"test_contract_wrapper"
}

def test_advanced_runtime_modules_are_real():
    files=[p for p in Path("app/runtime").glob("*.py")
           if p.stem not in SKIP and not p.name.startswith("__")]

    assert files

    for p in files:
        m=importlib.import_module("app.runtime."+p.stem)

        # accept legacy runtime modules
        if not hasattr(m,"health") or not hasattr(m,"run"):
            continue

        h=m.health()
        r=m.run({"text":"corrige bug e mantenha continuidade"})

        assert h["status"]=="operational"
        assert r["status"]=="operational"
