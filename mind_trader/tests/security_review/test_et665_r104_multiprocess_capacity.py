"""ET665.R104: independent processes must not exceed PAPER reservation capacity."""
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

PaperCapacityPrototype=runpy.run_path(str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py")))["PaperCapacityPrototype"]
CHILD = """
import runpy,sys
C=runpy.run_path(sys.argv[1])['PaperCapacityPrototype']
print(C(sys.argv[2]).reserve('s',sys.argv[3],1),flush=True)
"""

class R104Multiprocess(unittest.TestCase):
    def test_cross_process_capacity_and_idempotency(self):
        with tempfile.TemporaryDirectory(prefix="et665_r104_") as tmp:
            db=Path(tmp)/"capacity.sqlite"
            PaperCapacityPrototype(db)
            module=str(Path(__file__).with_name("et665_r95_atomic_capacity_prototype.py"))
            def submit(n):
                result=subprocess.run([sys.executable,"-I","-c",CHILD,module,str(db),"id-"+str(n)],
                                      capture_output=True,text=True,timeout=20,check=False)
                self.assertEqual(result.returncode,0,result.stderr)
                return result.stdout.strip()
            with ThreadPoolExecutor(max_workers=8) as pool:
                decisions=list(pool.map(submit,range(12)))
            self.assertEqual(decisions.count("RESERVED"),1)
            self.assertEqual(decisions.count("BLOCK_CAPACITY"),11)
            winner=decisions.index("RESERVED")
            self.assertEqual(submit(winner),"RESERVED")
            recovered=PaperCapacityPrototype(db)
            self.assertEqual(recovered.finalize("s","id-"+str(winner),True),"FILLED")
            self.assertEqual(recovered.count("s"),1)

if __name__=="__main__":
    unittest.main()
