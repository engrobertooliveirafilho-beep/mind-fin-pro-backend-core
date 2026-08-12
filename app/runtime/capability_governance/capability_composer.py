from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


MODE = "SHADOW_ONLY"

CORE_CAPABILITIES = {
    "distributed_task_orchestration": {
        "module": "app.api.eldora_async",
        "file": "app/api/eldora_async.py",
        "role": "distributed_task_orchestration",
    },
    "goal_planning_and_checkpointing": {
        "module": "app.api.eldora_autonomous",
        "file": "app/api/eldora_autonomous.py",
        "role": "goal_planning_and_checkpointing",
    },
    "semantic_memory_and_graph_access": {
        "module": "app.api.eldora_semantic",
        "file": "app/api/eldora_semantic.py",
        "role": "semantic_memory_and_graph_access",
    },
    "runtime_health_supervision": {
        "module": "app.api.eldora_runtime_supervisor",
        "file": "app/api/eldora_runtime_supervisor.py",
        "role": "runtime_health_supervision",
    },
    "auth_policy_and_tenant_guard": {
        "module": "app.api.eldora_security",
        "file": "app/api/eldora_security.py",
        "role": "auth_policy_and_tenant_guard",
    },
}

INTENT_CHAINS = {
    "design_or_automate_system": [
        "auth_policy_and_tenant_guard",
        "goal_planning_and_checkpointing",
        "semantic_memory_and_graph_access",
        "distributed_task_orchestration",
        "runtime_health_supervision",
    ],
    "generate_strategy_or_content": [
        "auth_policy_and_tenant_guard",
        "semantic_memory_and_graph_access",
        "goal_planning_and_checkpointing",
        "runtime_health_supervision",
    ],
    "diagnose_or_validate": [
        "auth_policy_and_tenant_guard",
        "runtime_health_supervision",
        "semantic_memory_and_graph_access",
        "goal_planning_and_checkpointing",
    ],
    "continue_current_mission": [
        "auth_policy_and_tenant_guard",
        "semantic_memory_and_graph_access",
        "goal_planning_and_checkpointing",
        "distributed_task_orchestration",
    ],
    "assist": [
        "auth_policy_and_tenant_guard",
        "semantic_memory_and_graph_access",
        "runtime_health_supervision",
    ],
}


@dataclass(frozen=True)
class CapabilityStep:
    order: int
    role: str
    module: str
    file: str
    mode: str
    production_allowed: bool
    direct_user_response_allowed: bool


def infer_intent(query: str) -> str:
    q = (query or "").lower()

    if any(x in q for x in ["automatizar", "criar sistema", "arquitetura", "pipeline", "orquestrar"]):
        return "design_or_automate_system"

    if any(x in q for x in ["estratégia", "marketing", "copy", "conteúdo", "vender", "lançamento"]):
        return "generate_strategy_or_content"

    if any(x in q for x in ["validar", "auditar", "erro", "bug", "falha", "diagnóstico", "pytest"]):
        return "diagnose_or_validate"

    if any(x in q for x in ["prossiga", "continue", "seguir", "retomar"]):
        return "continue_current_mission"

    return "assist"


def compose_capabilities(query: str, intent: str | None = None) -> Dict[str, Any]:
    selected_intent = intent or infer_intent(query)
    chain_roles = INTENT_CHAINS.get(selected_intent, INTENT_CHAINS["assist"])

    steps: List[CapabilityStep] = []
    for idx, role in enumerate(chain_roles, start=1):
        cap = CORE_CAPABILITIES[role]
        steps.append(
            CapabilityStep(
                order=idx,
                role=role,
                module=cap["module"],
                file=cap["file"],
                mode=MODE,
                production_allowed=False,
                direct_user_response_allowed=False,
            )
        )

    return {
        "mode": MODE,
        "query": query,
        "intent": selected_intent,
        "chain_length": len(steps),
        "capability_chain": [asdict(s) for s in steps],
        "final_authority_required": True,
        "execution_allowed": False,
        "shadow_only": True,
    }


if __name__ == "__main__":
    tests = [
        "como automatizar confinamento de boi",
        "crie estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "prossiga",
        "minha Mercedes não entra ré",
    ]

    import json
    for t in tests:
        print(json.dumps(compose_capabilities(t), indent=2, ensure_ascii=False))
