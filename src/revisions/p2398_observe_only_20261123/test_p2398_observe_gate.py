import unittest
from p2398_observe_gate import evaluate, GateRejected

BASE = dict(mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN",
            p2394_decision="OBSERVE_SCORE", p2395_decision="OBSERVE_ONLY",
            p2396_vote="OBSERVE_ONLY", real_execution_allowed=False,
            runtime_modification_allowed=False, operational_members=0, quorum_required=2)

class GateTests(unittest.TestCase):
    def test_observe_only(self):
        self.assertEqual(evaluate(BASE)["order_dispatch"], False)
        self.assertEqual(evaluate(BASE)["runtime_promotion"], False)
    def test_missing(self):
        for k in BASE:
            with self.subTest(k=k), self.assertRaises(GateRejected):
                evaluate({x:y for x,y in BASE.items() if x != k})
    def test_unsafe(self):
        for k,v in [("mode","LIVE"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),
                    ("p2394_decision","PROMOTE_SCORE"),("p2395_decision","PROMOTE"),
                    ("p2396_vote","OPERATE"),("real_execution_allowed",True),
                    ("runtime_modification_allowed",True),("operational_members",2),
                    ("quorum_required",1)]:
            with self.subTest(k=k), self.assertRaises(GateRejected):
                evaluate({**BASE,k:v})
    def test_bad_types(self):
        for k,v in [("operational_members",False),("quorum_required",True),("operational_members",0.0)]:
            with self.subTest(k=k), self.assertRaises(GateRejected):
                evaluate({**BASE,k:v})

if __name__ == "__main__":
    unittest.main()
