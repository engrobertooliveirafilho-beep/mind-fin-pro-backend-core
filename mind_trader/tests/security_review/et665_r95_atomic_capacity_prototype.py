"""R95 offline-only atomic PAPER capacity prototype; not wired to production.

SQLite BEGIN IMMEDIATE serializes capacity reservations across processes.
A unique order key makes reserve/commit/release idempotent.
"""
import sqlite3

class PaperCapacityPrototype:
    def __init__(self, path):
        self.path = str(path)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS orders (session TEXT NOT NULL, order_id TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('RESERVED','FILLED','REJECTED')), PRIMARY KEY(session,order_id))")

    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def reserve(self, session, order_id, limit):
        if not isinstance(session,str) or not session or not isinstance(order_id,str) or not order_id or type(limit) is not int or limit < 1:
            return "BLOCK_INVALID_RESERVATION"
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT state FROM orders WHERE session=? AND order_id=?", (session,order_id)).fetchone()
            if row:
                return "RESERVED" if row[0]=="RESERVED" else ("FILLED" if row[0]=="FILLED" else "BLOCK_REJECTED_ORDER")
            active=db.execute("SELECT COUNT(*) FROM orders WHERE session=? AND state IN ('RESERVED','FILLED')",(session,)).fetchone()[0]
            if active >= limit:
                return "BLOCK_CAPACITY"
            db.execute("INSERT INTO orders(session,order_id,state) VALUES(?,?,'RESERVED')",(session,order_id))
            return "RESERVED"

    def finalize(self, session, order_id, filled):
        if type(filled) is not bool:
            return "BLOCK_INVALID_FINALIZATION"
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT state FROM orders WHERE session=? AND order_id=?",(session,order_id)).fetchone()
            if not row:
                return "BLOCK_UNKNOWN_ORDER"
            if row[0]=="RESERVED":
                new_state="FILLED" if filled else "REJECTED"
                db.execute("UPDATE orders SET state=? WHERE session=? AND order_id=?",(new_state,session,order_id))
                return new_state
            return row[0]

    def count(self, session):
        with self._db() as db:
            return db.execute("SELECT COUNT(*) FROM orders WHERE session=? AND state='FILLED'",(session,)).fetchone()[0]
