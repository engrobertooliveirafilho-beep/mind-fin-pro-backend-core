"""ET665.R364 evidence report integrity and reproducibility tests."""
import copy,unittest
from mind_trader.experimental.et665_r364_evidence_builder import build
from app.agents._et665_r356_common import digest
class R364Evidence(unittest.TestCase):
    def test_real_19_output_records(self):
        r=build()
        self.assertEqual(r["candidate_count"],19)
        self.assertEqual(len(r["candidate_results"]),19)
        self.assertEqual(len({x["output_sha256"] for x in r["candidate_results"]}),19)
        for x in r["candidate_results"]:
            self.assertEqual(x["output_sha256"],digest(x["output"]))
            self.assertEqual(x["input_sha256"],r["input"]["input_sha256"])
        self.assertEqual(r["report_sha256"],digest({k:v for k,v in r.items() if k!="report_sha256"}))
    def test_deterministic(self):
        self.assertEqual(build()["report_sha256"],build()["report_sha256"])
    def test_no_promotion(self):
        r=build()
        self.assertFalse(r["official_hp19_certified"])
        self.assertFalse(r["phase_b_certified"])
        self.assertFalse(r["production_modified"])
        self.assertEqual(r["real_orders"],"FORBIDDEN")
    def test_report_tamper_detected(self):
        r=build();r["candidate_results"][0]["output"]["forged"]=True
        self.assertNotEqual(r["report_sha256"],digest({k:v for k,v in r.items() if k!="report_sha256"}))
if __name__=="__main__":unittest.main()
