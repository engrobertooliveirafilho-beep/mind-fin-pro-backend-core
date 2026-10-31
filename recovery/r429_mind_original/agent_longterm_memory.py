from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AgentEvent:
    ts: int
    session_id: str
    event: str


class AgentLongTermMemory:
    """
    Memória de longo prazo simples em memória para agentes.
    Agora com introspecção básica via collect_improvement_points.
    """

    def __init__(self) -> None:
        self._events_by_agent: Dict[str, List[AgentEvent]] = {}

    def add_event(self, agent_id: str, session_id: str, ts: int, event: str) -> None:
        events = self._events_by_agent.setdefault(agent_id, [])
        events.append(AgentEvent(ts=ts, session_id=session_id, event=event))

    def last_events(self, agent_id: str, limit: int = 50) -> List[str]:
        events = self._events_by_agent.get(agent_id, [])
        if not events:
            return []
        ordered = sorted(events, key=lambda e: e.ts)
        tail = ordered[-limit:]
        return [f"[{e.session_id}] {e.event}" for e in tail]

    def get_timeline(self, agent_id: str, limit: int = 50) -> List[str]:
        return self.last_events(agent_id, limit)

    # ===== introspecção =====

    def _custom_agent_introspection(self) -> List[str]:
        issues: List[str] = []

        if not self._events_by_agent:
            issues.append(
                "Nenhum evento registrado; memória de longo prazo está vazia. "
                "Avaliar se deveria persistir eventos em storage durável."
            )

        # exemplo de cheque simples: muitos eventos em memória de um único agente
        for agent_id, events in self._events_by_agent.items():
            if len(events) > 1000:
                issues.append(
                    f"Agente {agent_id} com {len(events)} eventos em memória; "
                    "considerar estratégia de compactação ou descarte."
                )

        return issues

    def collect_improvement_points(self) -> List[str]:
        """
        Retorna uma lista de textos descrevendo pontos de melhoria / peças faltantes
        relacionados à memória de longo prazo.
        """
        suggestions: List[str] = []

        name = getattr(self, "name", self.__class__.__name__)
        suggestions.append(f"[{name}] introspecção automática (memória de longo prazo)")

        total_agents = len(self._events_by_agent)
        suggestions.append(f"Total de agentes com histórico em memória: {total_agents}")

        if total_agents == 0:
            suggestions.append(
                "Memória não está sendo utilizada; verificar se os agentes "
                "estão de fato registrando eventos via add_event()."
            )
        else:
            for agent_id, events in self._events_by_agent.items():
                suggestions.append(
                    f"Agente {agent_id}: {len(events)} eventos registrados em memória."
                )

        # anexar issues específicas
        suggestions.extend(self._custom_agent_introspection())

        return suggestions

