import tempfile
import unittest
from pathlib import Path
from strict_replay import replay

class WalkForwardTests(unittest.TestCase):
    def test_missing_independent_hash_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data.csv"
            p.write_text("time,close\n2026-01-01T00:00:00Z,100\n2026-01-02T00:00:00Z,101\n2026-01-03T00:00:00Z,102\n")
            result=replay(p,expected_sha256=None,train_end="2026-01-01T00:00:00Z",test_start="2026-01-02T00:00:00Z",test_end="2026-01-03T00:00:00Z")
            self.assertEqual(result["status"],"BLOCKED")
            self.assertFalse(result["promotion_authorized"])
if __name__=="__main__":unittest.main()
