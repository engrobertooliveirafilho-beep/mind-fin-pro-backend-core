import unittest
from mind_trader.experimental.et665_r386_adversarial_chain import check_adversarial
class R386(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=check_adversarial()
    def test_corrupted_hash_rejected(self):self.assertEqual(self.result["cases"]["corrupted_agent_hash"],"REJECTED")
    def test_missing_agent_rejected(self):self.assertEqual(self.result["cases"]["missing_agent"],"REJECTED")
    def test_false_count_rejected(self):self.assertEqual(self.result["cases"]["false_agent_count"],"REJECTED")
    def test_no_false_certification(self):
        self.assertEqual(self.result["official_hp19_certified"],0)
        self.assertEqual(self.result["phase_b_certified"],0)
        self.assertEqual(self.result["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
