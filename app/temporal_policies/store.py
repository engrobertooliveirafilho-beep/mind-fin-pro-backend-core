from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TemporalPolicy:
    """
    STEP 534 - Politica com janela temporal.

    effective_from: inicio da vigencia (UTC)
    effective_to: fim da vigencia (UTC, opcional)
    """
    name: str
    version: int
    effective_from: datetime
    effective_to: Optional[datetime]
    payload: Dict[str, Any]


class TemporalPolicyStore:
    """
    STEP 534 - Armazena politicas com versionamento temporal.

    100% em memoria, isolado dos fluxos reais.
    """

    def __init__(self) -> None:
        self._by_name: Dict[str, List[TemporalPolicy]] = {}

    def _list_for(self, name: str) -> List[TemporalPolicy]:
        return self._by_name.setdefault(name, [])

    def add_policy(
        self,
        name: str,
        effective_from: datetime,
        effective_to: Optional[datetime],
        payload: Dict[str, Any],
    ) -> TemporalPolicy:
        items = self._list_for(name)
        version = 1 if not items else max(p.version for p in items) + 1
        policy = TemporalPolicy(
            name=name,
            version=version,
            effective_from=effective_from,
            effective_to=effective_to,
            payload=dict(payload),
        )
        items.append(policy)
        return policy

    def get_policy_at(self, name: str, at: datetime) -> Optional[TemporalPolicy]:
        """
        Retorna a politica valida naquele instante, se existir.
        """
        candidates = []
        for p in self._list_for(name):
            if p.effective_from <= at and (p.effective_to is None or at < p.effective_to):
                candidates.append(p)
        if not candidates:
            return None
        # se mais de uma, pega a de maior versao
        return max(candidates, key=lambda p: p.version)

