"""ET665.R113 — fail-closed PAPER capacity gate for isolated integration.

This adapter remains outside the original production gateway and supports only
explicitly configured offline PAPER tests. SQLite ledger is not a production
transaction coordinator: unknown outcomes retain capacity permanently.
"""
import sqlite3
import uuid
from pathlib import Path

class PaperCapacityGate:
    def __init__(self, path):
        self.path = str(path)
        if not self.path or self.path == ":memory:":
            raise ValueError("PERSISTENT_SQLITE_REQUIRED")
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS reservations ("
                       "session_id TEXT NOT NULL, order_id TEXT NOT NULL, state TEXT NOT NULL "
                       "CHECK(state IN ('RESERVED','FILLED','REJECTED')), "
                       "PRIMARY KEY(session_id,order_id))")

    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def reserve_new(self, session_id, limit):
        if not isinstance(session_id,str) or not session_id or type(limit) is not int or limit<1:
            return {"decision":"BLOCK_INVALID_CAPACITY"}
        try:
            with self._db() as db:
                db.execute("BEGIN IMMEDIATE")
                count=db.execute("SELECT COUNT(*) FROM reservations WHERE session_id=? "
                                 "AND state IN ('RESERVED','FILLED')",(session_id,)).fetchone()[0]
                if count>=limit:
                    return {"decision":"BLOCK_CAPACITY"}
                order_id=str(uuid.uuid4())
                db.execute("INSERT INTO reservations VALUES (?,?,'RESERVED')",(session_id,order_id))
                return {"decision":"RESERVED","session_id":session_id,"order_id":order_id}
        except sqlite3.Error:
            return {"decision":"BLOCK_CAPACITY_STORAGE"}

    def finalize(self, session_id, order_id, filled):
        if type(filled) is not bool or not isinstance(session_id,str) or not session_id or not isinstance(order_id,str) or not order_id:
            return "BLOCK_INVALID_FINALIZATION"
        try:
            with self._db() as db:
                db.execute("BEGIN IMMEDIATE")
                row=db.execute("SELECT state FROM reservations WHERE session_id=? AND order_id=?",
                               (session_id,order_id)).fetchone()
                if not row:
                    return "BLOCK_UNKNOWN_ORDER"
                if row[0]!="RESERVED":
                    return row[0]
                state="FILLED" if filled else "REJECTED"
                db.execute("UPDATE reservations SET state=? WHERE session_id=? AND order_id=?",
                           (state,session_id,order_id))
                return state
        except sqlite3.Error:
            return "BLOCK_CAPACITY_STORAGE"

    def remaining(self, session_id, limit):
        if not isinstance(session_id,str) or not session_id or type(limit) is not int or limit<1:
            return 0
        try:
            with self._db() as db:
                count=db.execute("SELECT COUNT(*) FROM reservations WHERE session_id=? AND state IN ('RESERVED','FILLED')",
                                 (session_id,)).fetchone()[0]
                return max(0,limit-count)
        except sqlite3.Error:
            return 0
