"""ET665.R369 evidence reproducibility and provenance regression."""
import copy,unittest
from decimal import Decimal
from mind_trader.experimental.et665_r369_portfolio_evidence import build
from app.agents._et665_r356_common import digest
class R369(unittest.TestCase):
    def test_three_strategies(self):
        r=build()
        self.assertEqual(r["strategy_count"],3)
        self.assertEqual(set(r["result"]["strategies"]),{"trend","countertrend","flat"})
        self.assertEqual(sum(map(Decimal,r["weights"].values())),Decimal(1))
    def test_integrity(self):
        r=build()
        self.assertEqual(r["input_sha256"],digest(r["inputs"]))
        self.assertEqual(r["evidence_sha256"],digest({k:v for k,v in r.items() if k!="evidence_sha256"}))
    def test_deterministic(self):
        self.assertEqual(build()["evidence_sha256"],build()["evidence_sha256"])
    def test_no_false_certification(self):
        r=build()
        self.assertFalse(r["official_hp19_certified"])
        self.assertFalse(r["phase_b_certified"])
        self.assertFalse(r["historical_p2405_integrated"])
        self.assertEqual(r["result"]["real_orders"],"FORBIDDEN")
    def test_tamper_detected(self):
        r=build();r["inputs"]["trend"][0]["close"]="999"
        self.assertNotEqual(r["input_sha256"],digest(r["inputs"]))
if __name__=="__main__":unittest.main()
