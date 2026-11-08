"""R99: recovery tests for offline-only SQLite PAPER capacity prototype."""
from pathlib import Path
import runpy
import tempfile
import unittest

PaperCapacityPrototype=runpy.run_path(str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py")))["PaperCapacityPrototype"]

class R99Recovery(unittest.TestCase):
    def test_reserved_capacity_survives_restart_and_replay(self):
        with tempfile.TemporaryDirectory(prefix="et665_r99_") as tmp:
            path=Path(tmp)/"capacity.sqlite"
            first=PaperCapacityPrototype(path)
            self.assertEqual(first.reserve("session","id-1",1),"RESERVED")
            del first
            restarted=PaperCapacityPrototype(path)
            self.assertEqual(restarted.reserve("session","id-1",1),"RESERVED")
            self.assertEqual(restarted.reserve("session","id-2",1),"BLOCK_CAPACITY")
            self.assertEqual(restarted.finalize("session","id-1",True),"FILLED")
            del restarted
            again=PaperCapacityPrototype(path)
            self.assertEqual(again.finalize("session","id-1",True),"FILLED")
            self.assertEqual(again.count("session"),1)
            self.assertEqual(again.reserve("session","id-2",1),"BLOCK_CAPACITY")

    def test_rejected_order_is_replay_safe_across_restart(self):
        with tempfile.TemporaryDirectory(prefix="et665_r99_") as tmp:
            path=Path(tmp)/"capacity.sqlite"
            store=PaperCapacityPrototype(path)
            self.assertEqual(store.reserve("session","bad",1),"RESERVED")
            self.assertEqual(store.finalize("session","bad",False),"REJECTED")
            del store
            restarted=PaperCapacityPrototype(path)
            self.assertEqual(restarted.finalize("session","bad",True),"REJECTED")
            self.assertEqual(restarted.reserve("session","bad",1),"BLOCK_REJECTED_ORDER")
            self.assertEqual(restarted.reserve("session","good",1),"RESERVED")
            self.assertEqual(restarted.finalize("session","good",True),"FILLED")
            self.assertEqual(restarted.count("session"),1)

if __name__=="__main__":
    unittest.main()
