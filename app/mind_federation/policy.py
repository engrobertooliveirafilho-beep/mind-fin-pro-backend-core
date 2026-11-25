from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FederationContract:
    """
    STEP 539 - Contrato de federacao entre MINDs.

    - remote_mind_id: identificador da instancia remota
    - allowed_topics: lista de topicos permitidos
    - max_sensitivity: nivel maximo (0–10) de sensibilidade permitida
    """
    remote_mind_id: str
    allowed_topics: List[str]
    max_sensitivity: int = 5
    meta: Optional[Dict[str, Any]] = None


class FederationPolicyEngine:
    """
    STEP 539 - Engine minima de federacao com policy.

    100% em memoria, isolada.
    """

    def __init__(self) -> None:
        self._contracts: Dict[str, FederationContract] = {}

    def register_contract(self, contract: FederationContract) -> None:
        if type(contract.max_sensitivity) is not int or not 0 <= contract.max_sensitivity <= 10:
            raise ValueError("Invalid contract sensitivity")
        self._contracts[contract.remote_mind_id] = deepcopy(contract)

    def get_contract(self, remote_mind_id: str) -> Optional[FederationContract]:
        return deepcopy(self._contracts.get(remote_mind_id))

    def can_share(self, remote_mind_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload esperado:
          - topic: str
          - sensitivity: int (0–10)
        """
        topic = str(payload.get("topic", "")).lower()
        sensitivity = payload.get("sensitivity")
        if type(sensitivity) is not int or not 0 <= sensitivity <= 10:
            return {"allowed": False, "reason": "Sensibilidade invalida ou ausente."}

        contract = self._contracts.get(remote_mind_id)
        if contract is None:
            return {
                "allowed": False,
                "reason": "Nenhum contrato de federacao encontrado.",
            }

        allowed_topics = [t.lower() for t in contract.allowed_topics]
        if topic not in allowed_topics:
            return {
                "allowed": False,
                "reason": "Topico nao permitido pelo contrato.",
            }

        if sensitivity > contract.max_sensitivity:
            return {
                "allowed": False,
                "reason": "Sensibilidade acima do permitido no contrato.",
            }

        return {
            "allowed": True,
            "reason": "Compartilhamento permitido pelo contrato de federacao.",
        }

