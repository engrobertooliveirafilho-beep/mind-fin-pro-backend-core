from __future__ import annotations
import importlib
from pathlib import Path

RUNTIME_MODULES = {}

def discover_runtime_modules() -> dict:
    runtime_path = Path(__file__).parent

    for file in runtime_path.glob("*.py"):

        if file.stem.startswith("__"):
            continue

        if file.stem in {
            "runtime_registry",
            "advanced_runtime_base"
        }:
            continue

        module_name=f"app.runtime.{file.stem}"

        try:
            module = importlib.import_module(module_name)

            if hasattr(module, "health") and hasattr(module, "run"):

                RUNTIME_MODULES[file.stem] = {
                    "module": module,
                    "health": module.health()
                }

        except Exception as e:
            RUNTIME_MODULES[file.stem] = {
                "error": str(e)
            }

    return RUNTIME_MODULES

def runtime_health_matrix() -> dict:
    return {
        k:v.get("health", {"status":"error"})
        for k,v in discover_runtime_modules().items()
    }
