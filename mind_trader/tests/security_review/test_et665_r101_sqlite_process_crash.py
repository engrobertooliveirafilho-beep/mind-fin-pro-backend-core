"""ET665.R101: offline SQLite process-crash transaction tests; no broker/network."""
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

PaperCapacityPrototype = runpy.run_path(str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py")))["PaperCapacityPrototype"]

CRASH_INSIDE_TX = """
import os,sqlite3,sys
db=sqlite3.connect(sys.argv[1], isolation_level=None)
db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO orders(session,order_id,state) VALUES('s','crashed','RESERVED')")
os._exit(71)
"""

CRASH_AFTER_COMMIT = """
import os,sqlite3,sys
db=sqlite3.connect(sys.argv[1], isolation_level=None)
db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO orders(session,order_id,state) VALUES('s','committed','RESERVED')")
db.execute('COMMIT')
os._exit(72)
"""

class R101ProcessCrash(unittest.TestCase):
    def _crash(self, script, path, expected):
        child = subprocess.run([sys.executable, "-I", "-c", script, str(path)],
                               capture_output=True, timeout=10, check=False)
        self.assertEqual(child.returncode, expected, child.stderr.decode(errors="replace"))

    def test_uncommitted_reservation_rolls_back_after_process_exit(self):
        with tempfile.TemporaryDirectory(prefix="et665_r101_") as tmp:
            path=Path(tmp)/"capacity.sqlite"
            PaperCapacityPrototype(path)
            self._crash(CRASH_INSIDE_TX,path,71)
            recovered=PaperCapacityPrototype(path)
            self.assertEqual(recovered.reserve("s","next",1),"RESERVED")
            self.assertEqual(recovered.count("s"),0)
            self.assertEqual(recovered.finalize("s","next",True),"FILLED")
            self.assertEqual(recovered.count("s"),1)

    def test_committed_reservation_survives_process_exit(self):
        with tempfile.TemporaryDirectory(prefix="et665_r101_") as tmp:
            path=Path(tmp)/"capacity.sqlite"
            PaperCapacityPrototype(path)
            self._crash(CRASH_AFTER_COMMIT,path,72)
            recovered=PaperCapacityPrototype(path)
            self.assertEqual(recovered.reserve("s","other",1),"BLOCK_CAPACITY")
            self.assertEqual(recovered.reserve("s","committed",1),"RESERVED")
            self.assertEqual(recovered.finalize("s","committed",True),"FILLED")
            self.assertEqual(recovered.count("s"),1)

if __name__=="__main__":
    unittest.main()
