"""ET665.R110 — offline PAPER reservation-to-fill correlation prototype.

No production imports, network access, real orders, or automatic recovery.
"""
import json
from pathlib import Path
import runpy
import tempfile
import unittest

Capacity = runpy.run_path(str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py")))["PaperCapacityPrototype"]

def paper_submit_offline(capacity, session, order_id, limit, ledger_path, simulate_filled=True):
    if not isinstance(session,str) or not session or not isinstance(order_id,str) or not order_id:
        return "BLOCK_INVALID_IDENTITY"
    if not isinstance(ledger_path,Path):
        return "BLOCK_INVALID_LEDGER"
    # Refuse ambiguous retries before reservation; never simulate a second fill.\n    with capacity._db() as db:\n        existing=db.execute("SELECT state FROM orders WHERE session=? AND order_id=?",(session,order_id)).fetchone()\n    if existing:\n        return "BLOCK_REPLAY_OR_CAPACITY"\n    state=capacity.reserve(session,order_id,limit)
    if state!="RESERVED":
        return "BLOCK_REPLAY_OR_CAPACITY" if state=="FILLED" else state
    # Replayed RESERVED must never simulate a second fill.
    # A new reservation cannot be distinguished from an ambiguous retry with
    # this prototype API; reject if any event for this order already exists.
    try:
        if ledger_path.exists():
            for line in ledger_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                event=json.loads(line)
                if not isinstance(event,dict):
                    return "BLOCK_LEDGER_INVALID"
                if event.get("session_id")==session and event.get("order_id")==order_id:
                    return "BLOCK_REPLAY_AMBIGUOUS"
    except (OSError,UnicodeError,ValueError):
        return "BLOCK_LEDGER_UNREADABLE"
    if simulate_filled is not True:
        return "BLOCK_UNCONFIRMED_FILL"
    event={"session_id":session,"order_id":order_id,"decision":"PAPER_ORDER_ACCEPTED",
           "order_status":"PAPER_FILLED_SIMULATED","fill":{"filled":True},
           "production":"BLOCKED","live":"FORBIDDEN"}
    try:
        with ledger_path.open("a",encoding="utf-8") as out:
            out.write(json.dumps(event,sort_keys=True)+"\n")
            out.flush()
            import os
            os.fsync(out.fileno())
    except OSError:
        return "BLOCK_LEDGER_WRITE_FAILED"
    final=capacity.finalize(session,order_id,True)
    return "PAPER_FILLED" if final=="FILLED" else "BLOCK_FINALIZATION"

class R110Correlation(unittest.TestCase):
    def test_capacity_precedes_fill_and_replay_blocks(self):
        with tempfile.TemporaryDirectory(prefix="et665_r110_") as tmp:
            store=Capacity(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"broker.jsonl"
            self.assertEqual(paper_submit_offline(store,"s","order-1",1,ledger),"PAPER_FILLED")
            self.assertEqual(paper_submit_offline(store,"s","order-2",1,ledger),"BLOCK_CAPACITY")
            self.assertEqual(paper_submit_offline(store,"s","order-1",1,ledger),"BLOCK_REPLAY_OR_CAPACITY")
            self.assertEqual(store.count("s"),1)
            self.assertEqual(len(ledger.read_text().splitlines()),1)

    def test_unconfirmed_fill_keeps_reservation(self):
        with tempfile.TemporaryDirectory(prefix="et665_r110_") as tmp:
            store=Capacity(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"broker.jsonl"
            self.assertEqual(paper_submit_offline(store,"s","order-1",1,ledger,False),"BLOCK_UNCONFIRMED_FILL")
            self.assertEqual(paper_submit_offline(store,"s","order-2",1,ledger),"BLOCK_CAPACITY")
            self.assertEqual(store.count("s"),0)

    def test_retry_after_unconfirmed_fill_stays_blocked(self):\n        with tempfile.TemporaryDirectory(prefix="et665_r110_") as tmp:\n            store=Capacity(Path(tmp)/"capacity.sqlite")\n            ledger=Path(tmp)/"broker.jsonl"\n            self.assertEqual(paper_submit_offline(store,"s","order-1",2,ledger,False),"BLOCK_UNCONFIRMED_FILL")\n            self.assertEqual(paper_submit_offline(store,"s","order-1",2,ledger),"BLOCK_REPLAY_OR_CAPACITY")\n            self.assertFalse(ledger.exists())\n\n    def test_invalid_ledger_does_not_release_reservation(self):
        with tempfile.TemporaryDirectory(prefix="et665_r110_") as tmp:
            store=Capacity(Path(tmp)/"capacity.sqlite")
            ledger=Path(tmp)/"broker.jsonl"
            ledger.write_text("{invalid",encoding="utf-8")
            self.assertEqual(paper_submit_offline(store,"s","order-1",1,ledger),"BLOCK_LEDGER_UNREADABLE")
            self.assertEqual(paper_submit_offline(store,"s","order-2",1,ledger),"BLOCK_CAPACITY")

if __name__=="__main__":
    unittest.main()
