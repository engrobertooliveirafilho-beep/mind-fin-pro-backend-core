from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional


EthicalStatus = Literal["pending", "approved", "rejected"]


@dataclass
class EthicalReviewItem:
    """
    STEP 542 - Item de revisão ética.
    """
    item_id: str
    payload: Dict[str, Any]
    status: EthicalStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer: Optional[str] = None
    notes: Optional[str] = None


class EthicalReviewBoard:
    """
    STEP 542 - Board minimo de revisão ética.

    100% em memória, isolado.
    """

    def __init__(self) -> None:
        self._items: Dict[str, EthicalReviewItem] = {}
        self._counter: int = 0

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _next_id(self) -> str:
        self._counter += 1
        return f"ERB-{self._counter}"

    def submit(self, payload: Dict[str, Any]) -> EthicalReviewItem:
        """
        Enfileira uma decisão sensível para revisão posterior.
        """
        item_id = self._next_id()
        item = EthicalReviewItem(
            item_id=item_id,
            payload=dict(payload),
            status="pending",
            created_at=self._now(),
        )
        self._items[item_id] = item
        return item

    def list_pending(self) -> List[EthicalReviewItem]:
        return [i for i in self._items.values() if i.status == "pending"]

    def _set_status(
        self,
        item_id: str,
        status: EthicalStatus,
        reviewer: Optional[str],
        notes: Optional[str],
    ) -> Optional[EthicalReviewItem]:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.status = status
        item.reviewer = reviewer
        item.notes = notes
        item.reviewed_at = self._now()
        return item

    def approve(self, item_id: str, reviewer: str, notes: Optional[str] = None) -> Optional[EthicalReviewItem]:
        return self._set_status(item_id, "approved", reviewer, notes)

    def reject(self, item_id: str, reviewer: str, notes: Optional[str] = None) -> Optional[EthicalReviewItem]:
        return self._set_status(item_id, "rejected", reviewer, notes)

