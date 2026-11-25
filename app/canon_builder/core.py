from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


CanonStatus = Literal["experimental", "canon"]


@dataclass
class CanonEntry:
    """
    STEP 533 - Entrada de conhecimento no Cânon.
    """
    key: str
    version: int
    status: CanonStatus
    payload: Dict[str, Any]


class CanonBuilder:
    """
    STEP 533 - Construtor minimo do Corpo de Conhecimento Oficial.

    - registra conhecimento como experimental
    - promove para canon
    - permite consumo filtrado apenas por canon
    """

    def __init__(self) -> None:
        self._entries: Dict[str, List[CanonEntry]] = {}

    def _get_list(self, key: str) -> List[CanonEntry]:
        return self._entries.setdefault(key, [])

    def add_experimental(self, key: str, payload: Dict[str, Any]) -> CanonEntry:
        items = self._get_list(key)
        version = 1 if not items else max(e.version for e in items) + 1
        entry = CanonEntry(key=key, version=version, status="experimental", payload=dict(payload))
        items.append(entry)
        return entry

    def promote_to_canon(self, key: str, version: Optional[int] = None) -> Optional[CanonEntry]:
        items = self._get_list(key)
        if not items:
            return None

        target: Optional[CanonEntry] = None
        if version is None:
            target = max(items, key=lambda e: e.version)
        else:
            for e in items:
                if e.version == version:
                    target = e
                    break

        if target is None:
            return None

        # Demarca todas as outras versoes como experimentais
        for e in items:
            if e is target:
                e.status = "canon"
            else:
                if e.status == "canon":
                    e.status = "experimental"

        return target

    def get_latest_canon(self, key: str) -> Optional[CanonEntry]:
        items = [e for e in self._get_list(key) if e.status == "canon"]
        if not items:
            return None
        return max(items, key=lambda e: e.version)

