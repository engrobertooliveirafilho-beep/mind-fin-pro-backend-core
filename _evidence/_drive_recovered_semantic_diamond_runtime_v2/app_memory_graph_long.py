from dataclasses import dataclass
from typing import List

@dataclass
class TimelineEvent:
    session_id: str
    content: str

class LongTermGraphMemory:
    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self._events: List[TimelineEvent] = []

    def add_event(self, session_id: str, content: str) -> None:
        self._events.append(TimelineEvent(session_id=session_id, content=content))
        if len(self._events) > self.max_items:
            self._events = self._events[-self.max_items:]

    def get_last_events(self, limit: int = 50):
        return self._events[-limit:]
