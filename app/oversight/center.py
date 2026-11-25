from datetime import datetime
from typing import Dict, Any, List


class OversightRecord:
    """
    STEP 521 - Representa um registro de uma decisão crítica.
    Não salva em banco (versão mínima, apenas em memória).
    """

    def __init__(self, decision_id: str, payload: Dict[str, Any], reviewer: str = None):
        self.decision_id = decision_id
        self.payload = payload
        self.reviewer = reviewer
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "payload": self.payload,
            "reviewer": self.reviewer,
            "timestamp": self.timestamp.isoformat() + "Z",
        }


class HumanOversightCenter:
    """
    STEP 521 - Núcleo do Human Oversight Center.
    Apenas registra decisões, sem afetar a lógica existente.
    """

    def __init__(self):
        self._records: List[OversightRecord] = []

    def submit(self, decision_id: str, payload: Dict[str, Any]) -> OversightRecord:
        record = OversightRecord(decision_id, payload)
        self._records.append(record)
        return record

    def list_records(self) -> List[OversightRecord]:
        return self._records[:]

