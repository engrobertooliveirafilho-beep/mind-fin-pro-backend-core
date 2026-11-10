from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MultiAgentRole(str, Enum):
    USER = "user"
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    TOOLMASTER = "toolmaster"
    SUMMARIZER = "summarizer"


@dataclass
class MultiAgentMessage:
    role: MultiAgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiAgentConfig:
    """
    Configuração do sistema multi-agente.

    max_rounds controla quantos ciclos completos a pipeline executa:
    USER -> ORCHESTRATOR -> RESEARCHER -> TOOLMASTER -> SUMMARIZER
    """

    max_rounds: int = 1

    # ===== introspecção =====

    def _custom_agent_introspection(self) -> List[str]:
        issues: List[str] = []

        # Exemplo de futuros campos que podem virar padrão:
        # if not hasattr(self, "topology"):
        #     issues.append("topology não definida para o sistema multi-agente.")
        # if not hasattr(self, "coordination_strategy"):
        #     issues.append("coordination_strategy ausente; definir estratégia de coordenação entre agentes.")

        return issues

    def collect_improvement_points(self) -> List[str]:
        """
        Retorna uma lista de textos descrevendo pontos de melhoria / peças faltantes
        relacionados à configuração multi-agente.
        """
        suggestions: List[str] = []

        name = getattr(self, "name", self.__class__.__name__)
        suggestions.append(f"[{name}] introspecção automática (config multi-agente)")
        suggestions.append(f"max_rounds configurado: {self.max_rounds}")

        if self.max_rounds < 1:
            suggestions.append(
                "max_rounds < 1; isto pode quebrar o fluxo multi-agente. "
                "Recomenda-se max_rounds >= 1."
            )
        elif self.max_rounds == 1:
            suggestions.append(
                "max_rounds = 1; sistema roda apenas um ciclo. Avaliar se faz sentido permitir iterações adicionais."
            )
        else:
            suggestions.append(
                "max_rounds > 1; garantir que os agentes lidam bem com histórico crescente."
            )

        # Campos opcionais que você pode decidir implementar mais tarde
        if hasattr(self, "topology"):
            suggestions.append(f"topology definido: {getattr(self, 'topology')}")
        else:
            suggestions.append(
                "topology não definido; avaliar se deveria modelar a topologia "
                "(pipeline, grafo, árvore, etc.)."
            )

        if hasattr(self, "coordination_strategy"):
            suggestions.append(
                f"coordination_strategy definido: {getattr(self, 'coordination_strategy')}"
            )
        else:
            suggestions.append(
                "coordination_strategy ausente; definir como os agentes coordenam entre si "
                "(ex: round-robin, prioridade, score, votação)."
            )

        # Hook customizado
        suggestions.extend(self._custom_agent_introspection())

        return suggestions


AgentFn = Callable[[List[MultiAgentMessage]], MultiAgentMessage]


class MultiAgentSystem:
    """
    Sistema multi-agente cooperativo:

      USER -> ORCHESTRATOR -> RESEARCHER -> TOOLMASTER -> SUMMARIZER
    """

    def __init__(
        self,
        orchestrator: AgentFn,
        researcher: AgentFn,
        toolmaster: AgentFn,
        summarizer: AgentFn,
        config: Optional[MultiAgentConfig] = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.researcher = researcher
        self.toolmaster = toolmaster
        self.summarizer = summarizer
        self.config = config or MultiAgentConfig()

    def run(self, user_message: str) -> List[MultiAgentMessage]:
        history: List[MultiAgentMessage] = [
            MultiAgentMessage(role=MultiAgentRole.USER, content=user_message, metadata={})
        ]

        for _ in range(max(1, self.config.max_rounds)):
            o_msg = self.orchestrator(history)
            if o_msg.role != MultiAgentRole.ORCHESTRATOR:
                raise ValueError("orchestrator agent must return role=ORCHESTRATOR")
            history.append(o_msg)

            r_msg = self.researcher(history)
            if r_msg.role != MultiAgentRole.RESEARCHER:
                raise ValueError("researcher agent must return role=RESEARCHER")
            history.append(r_msg)

            t_msg = self.toolmaster(history)
            if t_msg.role != MultiAgentRole.TOOLMASTER:
                raise ValueError("toolmaster agent must return role=TOOLMASTER")
            history.append(t_msg)

            s_msg = self.summarizer(history)
            if s_msg.role != MultiAgentRole.SUMMARIZER:
                raise ValueError("summarizer agent must return role=SUMMARIZER")
            history.append(s_msg)

        return history

