from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .multi_agent import MultiAgentConfig


class MultiAgentRole(Enum):
    """
    Papéis padrão do sistema multi-agente usados nos testes.
    """

    USER = "user"
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    TOOLMASTER = "toolmaster"
    SUMMARIZER = "summarizer"


@dataclass
class MultiAgentMessage:
    """
    Mensagem usada no fluxo do sistema multi-agente.

    Nos testes, só são usados:
    - role: MultiAgentRole
    - content: texto
    """

    role: MultiAgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiAgentSystem:
    """
    Sistema multi-agente minimalista, compatível com os testes.

    Construtor recebe handlers nomeados:

    - orchestrator(history) -> MultiAgentMessage
    - researcher(history)   -> MultiAgentMessage
    - toolmaster(history)   -> MultiAgentMessage
    - summarizer(history)   -> MultiAgentMessage

    e uma MultiAgentConfig com max_rounds.
    """

    def __init__(
        self,
        *,
        orchestrator: Callable[[List[MultiAgentMessage]], MultiAgentMessage],
        researcher: Callable[[List[MultiAgentMessage]], MultiAgentMessage],
        toolmaster: Callable[[List[MultiAgentMessage]], MultiAgentMessage],
        summarizer: Callable[[List[MultiAgentMessage]], MultiAgentMessage],
        config: Optional[MultiAgentConfig] = None,
        **_: Any,
    ) -> None:
        self.config: MultiAgentConfig = config or MultiAgentConfig()
        self._orchestrator = orchestrator
        self._researcher = researcher
        self._toolmaster = toolmaster
        self._summarizer = summarizer

    # ------------------------------------------------------------------
    # 1 round único (ignora max_rounds) — usado por test_single_round
    # ------------------------------------------------------------------
    def run_single_round(self, user_content: str) -> List[MultiAgentMessage]:
        """
        Executa exatamente 1 round:

        USER -> ORCHESTRATOR -> RESEARCHER -> TOOLMASTER -> SUMMARIZER
        """
        history: List[MultiAgentMessage] = []

        user_msg = MultiAgentMessage(
            role=MultiAgentRole.USER,
            content=user_content,
        )
        history.append(user_msg)

        orch_msg = self._orchestrator(history)
        history.append(orch_msg)

        res_msg = self._researcher(history)
        history.append(res_msg)

        tool_msg = self._toolmaster(history)
        history.append(tool_msg)

        sum_msg = self._summarizer(history)
        history.append(sum_msg)

        return history

    # ------------------------------------------------------------------
    # Múltiplos rounds — respeita config.max_rounds
    # ------------------------------------------------------------------
    def run(self, user_content: str) -> List[MultiAgentMessage]:
        """
        Executa 1 ou mais rounds, de acordo com config.max_rounds.

        Round 0: mensagem do USER
        Para cada round:
            ORCHESTRATOR -> RESEARCHER -> TOOLMASTER -> SUMMARIZER

        Exemplo esperado no teste:
        max_rounds=2 => 1 user + 4*2 agentes = 9 mensagens.
        """
        history: List[MultiAgentMessage] = []

        # mensagem inicial do usuário
        user_msg = MultiAgentMessage(
            role=MultiAgentRole.USER,
            content=user_content,
        )
        history.append(user_msg)

        rounds = getattr(self.config, "max_rounds", 1) or 1
        try:
            rounds = int(rounds)
        except Exception:
            rounds = 1
        if rounds < 1:
            rounds = 1

        for _ in range(rounds):
            orch_msg = self._orchestrator(history)
            history.append(orch_msg)

            res_msg = self._researcher(history)
            history.append(res_msg)

            tool_msg = self._toolmaster(history)
            history.append(tool_msg)

            sum_msg = self._summarizer(history)
            history.append(sum_msg)

        return history

