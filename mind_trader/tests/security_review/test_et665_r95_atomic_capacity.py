"""R95 atomic capacity characterization: concurrent reservations, idempotency, rejection."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from et665_r95_atomic_capacity_prototype import PaperCapacityPrototype

class R95AtomicCapacity(unittest.TestCase):
    def test_concurrent_reservations_and_idempotent_fill(self):
        with tempfile.TemporaryDirectory(prefix="et665_r95_") as tmp:
            store=PaperCapacityPrototype(Path(tmp)/"capacity.sqlite")
            with ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda n: store.reserve("session","order-"+str(n),1),range(16)))
            self.assertEqual(results.count("RESERVED"),1)
            self.assertEqual(results.count("BLOCK_CAPACITY"),15)
            winner=results.index("RESERVED")
            key="order-"+str(winner)
            self.assertEqual(store.reserve("session",key,1),"RESERVED")
            self.assertEqual(store.finalize("session",key,True),"FILLED")
            self.assertEqual(store.finalize("session",key,True),"FILLED")
            self.assertEqual(store.reserve("session",key,1),"FILLED")
            self.assertEqual(store.count("session"),1)
            self.assertEqual(store.reserve("session","later",1),"BLOCK_CAPACITY")

    def test_rejected_reservation_releases_capacity(self):
        with tempfile.TemporaryDirectory(prefix="et665_r95_") as tmp:
            store=PaperCapacityPrototype(Path(tmp)/"capacity.sqlite")
            self.assertEqual(store.reserve("s","bad",1),"RESERVED")
            self.assertEqual(store.finalize("s","bad",False),"REJECTED")
            self.assertEqual(store.finalize("s","bad",True),"REJECTED")
            self.assertEqual(store.reserve("s","bad",1),"BLOCK_REJECTED_ORDER")
            self.assertEqual(store.count("s"),0)
            self.assertEqual(store.reserve("s","good",1),"RESERVED")
            self.assertEqual(store.finalize("s","good",True),"FILLED")
            self.assertEqual(store.count("s"),1)
            self.assertEqual(store.finalize("s","missing",True),"BLOCK_UNKNOWN_ORDER")

if __name__=="__main__":
    unittest.main()
