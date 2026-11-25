from dataclasses import dataclass
from typing import Any, Dict, List, Literal


TreatyStatus = Literal["accepted", "rejected"]


@dataclass
class Treaty:
    """
    STEP 540 - Representa um tratado cognitivo entre partes.
    """
    parties: List[str]
    terms: Dict[str, Any]


@dataclass
class TreatyResult:
    """
    STEP 540 - Resultado da negociacao do tratado.
    """
    status: TreatyStatus
    reason: str
    agreed_terms: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "agreed_terms": self.agreed_terms,
        }


class CognitiveTreatyProtocol:
    """
    STEP 540 - Protocolo minimo de tratados cognitivos.

    Regras simples para este STEP:
    - se proposal["mode"] == "cooperation" e nao houver "aggression" em topics -> accepted
    - se houver "aggression" ou "unbounded_access" em topics -> rejected
    """

    def negotiate(self, parties: List[str], proposal: Dict[str, Any]) -> TreatyResult:
        topics = [str(t).lower() for t in proposal.get("topics", [])]
        mode = str(proposal.get("mode", "cooperation")).lower()

        if any(t in ("aggression", "unbounded_access") for t in topics):
            return TreatyResult(
                status="rejected",
                reason="Proposta contem topicos proibidos (aggression/unbounded_access).",
                agreed_terms={},
            )

        sensitivity = proposal.get("max_data_sensitivity", 5)
        if type(sensitivity) is not int or not 0 <= sensitivity <= 10:
            return TreatyResult("rejected", "Sensibilidade invalida.", {})

        if mode == "cooperation":
            agreed_terms = {
                "mode": "cooperation",
                "max_data_sensitivity": sensitivity,
                "shared_topics": topics,
                "parties": list(parties),
            }
            return TreatyResult(
                status="accepted",
                reason="Tratado de cooperacao aceito dentro dos limites basicos.",
                agreed_terms=agreed_terms,
            )

        # default conservador
        return TreatyResult(
            status="rejected",
            reason="Modo de tratado nao suportado neste STEP.",
            agreed_terms={},
        )

