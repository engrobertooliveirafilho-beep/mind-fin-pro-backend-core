"""Recovered AgentLongTermMemory with optional SQLite durability.

The original in-memory API remains the default. Set db_path explicitly to enable
cross-instance persistence; no implicit files or network access are created.
"""
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional

@dataclass
class AgentEvent:
    ts: int
    session_id: str
    event: str

class AgentLongTermMemory:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self._events_by_agent: Dict[str, List[AgentEvent]] = {}
        self._db_path = Path(db_path).expanduser().absolute() if db_path is not None else None
        if self._db_path is not None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_store()

    def _connect(self):
        assert self._db_path is not None
        return sqlite3.connect(str(self._db_path), timeout=5.0)

    def _initialize_store(self) -> None:
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS agent_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                ts INTEGER NOT NULL,
                event TEXT NOT NULL
            )""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_events_agent_id_id ON agent_events(agent_id, id)")

    @staticmethod
    def _validate_event(agent_id: str, session_id: str, ts: int, event: str) -> None:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(ts, int) or isinstance(ts, bool):
            raise ValueError("ts must be an integer")
        if not isinstance(event, str):
            raise ValueError("event must be a string")

    def add_event(self, agent_id: str, session_id: str, ts: int, event: str) -> None:
        self._validate_event(agent_id, session_id, ts, event)
        if self._db_path is not None:
            with self._connect() as conn:
                conn.execute("INSERT INTO agent_events(agent_id, session_id, ts, event) VALUES (?, ?, ?, ?)",
                             (agent_id, session_id, ts, event))
        else:
            self._events_by_agent.setdefault(agent_id, []).append(AgentEvent(ts, session_id, event))

    def last_events(self, agent_id: str, limit: int = 50) -> List[str]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("limit must be a non-negative integer")
        if limit == 0:
            return []
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        if self._db_path is not None:
            with self._connect() as conn:
                rows = conn.execute("SELECT session_id, event FROM agent_events WHERE agent_id=? ORDER BY ts DESC, id DESC LIMIT ?",
                                    (agent_id, limit)).fetchall()
            rows.reverse()
            return [f"[{session_id}] {event}" for session_id, event in rows]
        events = self._events_by_agent.get(agent_id, [])
        ordered = sorted(events, key=lambda e: e.ts)
        return [f"[{e.session_id}] {e.event}" for e in ordered[-limit:]]

    def get_timeline(self, agent_id: str, limit: int = 50) -> List[str]:
        return self.last_events(agent_id, limit)

    def _custom_agent_introspection(self) -> List[str]:
        issues: List[str] = []
        if self._db_path is not None:
            with self._connect() as conn:
                rows = conn.execute("SELECT agent_id, COUNT(*) FROM agent_events GROUP BY agent_id").fetchall()
            counts = dict(rows)
        else:
            counts = {agent_id: len(events) for agent_id, events in self._events_by_agent.items()}
        if not counts:
            issues.append("Nenhum evento registrado; memória de longo prazo está vazia.")
        for agent_id, count in counts.items():
            if count > 1000:
                issues.append(f"Agente {agent_id} com {count} eventos; considerar compactação ou descarte.")
        return issues

    def collect_improvement_points(self) -> List[str]:
        suggestions = [f"[{getattr(self, 'name', self.__class__.__name__)}] introspecção automática (memória de longo prazo)"]
        if self._db_path is not None:
            with self._connect() as conn:
                rows = conn.execute("SELECT agent_id, COUNT(*) FROM agent_events GROUP BY agent_id").fetchall()
            counts = dict(rows)
        else:
            counts = {agent_id: len(events) for agent_id, events in self._events_by_agent.items()}
        suggestions.append(f"Total de agentes com histórico: {len(counts)}")
        for agent_id, count in counts.items():
            suggestions.append(f"Agente {agent_id}: {count} eventos registrados.")
        suggestions.extend(self._custom_agent_introspection())
        return suggestions
