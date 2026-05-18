from __future__ import annotations
from typing import Any
from app.runtime.advanced_runtime_base import AdvancedRuntimeEngine

class NaturalTransitionEngine(AdvancedRuntimeEngine):
    module_name = "natural_transition_engine"
    domain = "dialogue"

    def _signals(self, payload: dict[str, Any]) -> dict[str, Any]:
        signals = super()._signals(payload)
        text = str((payload or {}).get("text") or (payload or {}).get("message") or "").lower()
        signals.update({
            "contains_question": "?" in text or any(x in text for x in ["como", "qual", "por que", "quando"]),
            "contains_risk": any(x in text for x in ["erro", "falha", "bug", "risco", "alucina"]),
            "contains_memory_need": any(x in text for x in ["lembra", "contexto", "continuidade", "histórico"]),
            "contains_action_need": any(x in text for x in ["faça", "executa", "cria", "corrige", "implanta"]),
        })
        return signals

def health() -> dict[str, Any]:
    return NaturalTransitionEngine().health()

def run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return NaturalTransitionEngine().run(payload)
