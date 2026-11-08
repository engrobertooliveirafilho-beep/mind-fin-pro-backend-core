"""ET665.R106: fail-closed reconciliation contracts for PAPER capacity prototype.

No gateway, broker, network or real-order access. Ledger is a local JSONL fixture.
"""
import json
from pathlib import Path
import runpy
import tempfile
import unittest

PaperCapacityPrototype = runpy.run_path(str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py")))["PaperCapacityPrototype"]

def reconcile_capacity(store, session, ledger):
    """Read-only reconciliation. Never auto-release ambiguous reservations."""
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
        events = [json.loads(line) for line in lines if line.strip()]
    except (OSError, UnicodeError, ValueError):
        return {"decision":"BLOCK_LEDGER_UNREADABLE"}
    if not all(isinstance(event,dict) and isinstance(event.get("order_id"),str)
               and isinstance(event.get("state"),str) for event in events):
        return {"decision":"BLOCK_LEDGER_INVALID"}
    ids = [event["order_id"] for event in events if event["state"]=="FILLED"]
    if len(ids)!=len(set(ids)):
        return {"decision":"BLOCK_LEDGER_DUPLICATE_FILL"}
    with store._db() as db:
        rows = db.execute("SELECT order_id,state FROM orders WHERE session=?",(session,)).fetchall()
    reserved = [order_id for order_id,state in rows if state=="RESERVED"]
    filled = {order_id for order_id,state in rows if state=="FILLED"}
    if reserved:
        return {"decision":"BLOCK_UNRESOLVED_RESERVATIONS","count":len(reserved)}
    if set(ids)!=filled:
        return {"decision":"BLOCK_LEDGER_MISMATCH","ledger_count":len(ids),"sqlite_count":len(filled)}
    return {"decision":"RECONCILED","count":len(filled)}

class R106Reconciliation(unittest.TestCase):
    def test_matching_ledger(self):
        with tempfile.TemporaryDirectory(prefix="et665_r106_") as tmp:
            store=PaperCapacityPrototype(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"ledger.jsonl"
            self.assertEqual(store.reserve("s","one",1),"RESERVED")
            self.assertEqual(store.finalize("s","one",True),"FILLED")
            ledger.write_text(json.dumps({"order_id":"one","state":"FILLED"})+"\n",encoding="utf-8")
            self.assertEqual(reconcile_capacity(store,"s",ledger),{"decision":"RECONCILED","count":1})

    def test_orphan_reservation_blocks(self):
        with tempfile.TemporaryDirectory(prefix="et665_r106_") as tmp:
            store=PaperCapacityPrototype(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"ledger.jsonl"
            self.assertEqual(store.reserve("s","orphan",1),"RESERVED")
            ledger.write_text("",encoding="utf-8")
            self.assertEqual(reconcile_capacity(store,"s",ledger)["decision"],"BLOCK_UNRESOLVED_RESERVATIONS")
            self.assertEqual(store.reserve("s","next",1),"BLOCK_CAPACITY")

    def test_missing_or_duplicate_fill_blocks(self):
        with tempfile.TemporaryDirectory(prefix="et665_r106_") as tmp:
            store=PaperCapacityPrototype(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"ledger.jsonl"
            store.reserve("s","one",1)
            store.finalize("s","one",True)
            ledger.write_text("",encoding="utf-8")
            self.assertEqual(reconcile_capacity(store,"s",ledger)["decision"],"BLOCK_LEDGER_MISMATCH")
            row=json.dumps({"order_id":"one","state":"FILLED"})+"\n"
            ledger.write_text(row+row,encoding="utf-8")
            self.assertEqual(reconcile_capacity(store,"s",ledger)["decision"],"BLOCK_LEDGER_DUPLICATE_FILL")
            ledger.write_text("{bad",encoding="utf-8")
            self.assertEqual(reconcile_capacity(store,"s",ledger)["decision"],"BLOCK_LEDGER_UNREADABLE")

if __name__=="__main__":
    unittest.main()
