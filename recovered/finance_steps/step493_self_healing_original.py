from datetime import datetime, timezone
from typing import Dict, List, Tuple

from .healing_models import (
    SubsystemHealth,
    HealingAction,
    health_to_dict,
    action_to_dict,
)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_health_state() -> List[SubsystemHealth]:
    # Estado 100% simulado. Nada conectado a infra real.
    return [
        SubsystemHealth(
            id="db-core",
            name="Banco de dados principal",
            domain="infrastructure",
            health_score=0.82,
            severity="medium",
            description="Latency moderada e poucos erros intermitentes.",
        ),
        SubsystemHealth(
            id="agents-exec",
            name="Execução de agentes cognitivos",
            domain="agents",
            health_score=0.55,
            severity="high",
            description="Algumas filas com tempo de espera elevado.",
        ),
        SubsystemHealth(
            id="biz-pipeline",
            name="Pipeline de negócio",
            domain="business",
            health_score=0.68,
            severity="medium",
            description="Conversão abaixo da meta em campanhas recentes.",
        ),
    ]


def _derive_healing_actions(health_state: List[SubsystemHealth]) -> List[HealingAction]:
    actions: List[HealingAction] = []

    for h in health_state:
        if h.health_score >= 0.75:
            # Considerado saudável o suficiente, nenhuma ação de cura crítica
            continue

        if h.id == "agents-exec":
            actions.append(
                HealingAction(
                    id="heal-agents-queues",
                    target_subsystem_id=h.id,
                    title="Rebalancear filas de agentes e revisar timeouts",
                    description="Rever configuração de filas, timeouts e número de workers lógicos.",
                    automated_possible=False,
                    playbook_ref="PLAYBOOK-AGENTS-QUEUES-v1",
                )
            )
        elif h.id == "db-core":
            actions.append(
                HealingAction(
                    id="heal-db-observability",
                    target_subsystem_id=h.id,
                    title="Reforçar observabilidade do banco",
                    description="Ajustar limites de conexões e analisar queries mais lentas.",
                    automated_possible=False,
                    playbook_ref="PLAYBOOK-DB-OBS-v1",
                )
            )
        elif h.id == "biz-pipeline":
            actions.append(
                HealingAction(
                    id="heal-biz-funnel",
                    target_subsystem_id=h.id,
                    title="Rever funil de aquisição e qualificação de leads",
                    description="Checar etapas com maior perda e testar novas variações.",
                    automated_possible=False,
                    playbook_ref="PLAYBOOK-BIZ-FUNNEL-v1",
                )
            )

    return actions


def get_self_healing_snapshot() -> Dict:
    health_state = _mock_health_state()
    actions = _derive_healing_actions(health_state)

    return {
        "version": "step493-v1",
        "generated_at": _now_utc_iso(),
        "status": "ok",
        "subsystems": [health_to_dict(h) for h in health_state],
        "actions": [action_to_dict(a) for a in actions],
    }

