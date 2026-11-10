import unittest
from mind_trader.experimental.et665_r371_historical_source_gate import inspect_source
class R371(unittest.TestCase):
    def test_static_historical_script(self):
        src='MISSION="P2405E3"\nMODE="PAPER_ONLY"\nREAL_ORDERS="FORBIDDEN"\nFTMO_REAL="FORBIDDEN"\nfor x in []: pass\n'
        r=inspect_source(src)
        self.assertFalse(r["safe_to_import"])
        self.assertEqual(r["import_side_effect_lines"],[5])
    def test_missing_lock_rejected(self):
        with self.assertRaises(ValueError):
            inspect_source('MODE="PAPER_ONLY"\nREAL_ORDERS="FORBIDDEN"\nfor x in []: pass')
    def test_real_orders_rejected(self):
        with self.assertRaises(ValueError):
            inspect_source('MODE="PAPER_ONLY"\nREAL_ORDERS="ALLOWED"\nFTMO_REAL="FORBIDDEN"\nfor x in []: pass')
    def test_no_side_effects_rejected(self):
        with self.assertRaises(ValueError):
            inspect_source('MODE="PAPER_ONLY"\nREAL_ORDERS="FORBIDDEN"\nFTMO_REAL="FORBIDDEN"')
if __name__=="__main__":unittest.main()
