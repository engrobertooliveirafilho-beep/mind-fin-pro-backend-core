from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


KnowledgeStatus = Literal["active", "deprecated"]


@dataclass
class KnowledgeItem:
    """
    STEP 532 - Representa um núcleo de conhecimento versionado.
    """
    key: str
    version: int
    status: KnowledgeStatus
    payload: Dict[str, Any]


class KnowledgeLifecycleManager:
    """
    STEP 532 - Gestor minimo do ciclo de vida do conhecimento.

    100% em memoria.
    """

    def __init__(self) -> None:
        self._items: Dict[str, List[KnowledgeItem]] = {}

    def _get_list(self, key: str) -> List[KnowledgeItem]:
        return self._items.setdefault(key, [])

    def create(self, key: str, payload: Dict[str, Any]) -> KnowledgeItem:
        lst = self._get_list(key)
        version = 1 if not lst else max(i.version for i in lst) + 1
        item = KnowledgeItem(key=key, version=version, status="active", payload=dict(payload))
        lst.append(item)
        return item

    def revise(self, key: str, payload: Dict[str, Any]) -> KnowledgeItem:
        """
        Cria nova versao e deixa as anteriores como active por enquanto.
        Evolucoes futuras (outros STEPs) podem alterar essa politica.
        """
        return self.create(key, payload)

    def deprecate(self, key: str, version: Optional[int] = None) -> None:
        lst = self._get_list(key)
        for item in lst:
            if version is None or item.version == version:
                item.status = "deprecated"

    def get_latest_active(self, key: str) -> Optional[KnowledgeItem]:
        lst = [i for i in self._get_list(key) if i.status == "active"]
        if not lst:
            return None
        return max(lst, key=lambda i: i.version)

