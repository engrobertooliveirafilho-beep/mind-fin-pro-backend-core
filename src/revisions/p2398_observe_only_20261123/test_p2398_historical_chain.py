import json
import pathlib
import unittest
from p2398_historical_chain import evaluate_historical_chain
from p2398_observe_gate import GateRejected
HERE=pathlib.Path(__file__).resolve().parent
class ChainTests(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((HERE/"p2394_original_summary.json").read_text())
        self.r=json.loads((HERE/"router_contract.json").read_text())
        self.e=json.loads((HERE/"ensemble_result.json").read_text())
    def test_historical_observe_chain(self):
        result=evaluate_historical_chain(self.p,self.r,self.e)
        self.assertEqual(result["decision"],"OBSERVE_ONLY")
        self.assertFalse(result["order_dispatch"])
    def test_p2394_mutation_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_historical_chain({**self.p,"real_execution_allowed":True},self.r,self.e)
    def test_score_mismatch_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_historical_chain(self.p,{**self.r,"input_edge_score":69},self.e)
    def test_ensemble_member_mismatch_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_historical_chain(self.p,self.r,{**self.e,"members":2})
    def test_ensemble_quorum_mismatch_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_historical_chain(self.p,self.r,{**self.e,"operational_members":1})
    def test_missing_quorum_fails_closed(self):
        bad = dict(self.e)
        del bad['quorum']
        with self.assertRaises(GateRejected):
            evaluate_historical_chain(self.p,self.r,bad)
    def test_missing_members_fails_closed(self):
        bad = dict(self.e)
        del bad['members']
        with self.assertRaises(GateRejected):
            evaluate_historical_chain(self.p,self.r,bad)
    def test_promoted_edge_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_historical_chain({**self.p,"best_scored_edge":{**self.p["best_scored_edge"],"decision":"PROMOTE_SCORE"}},self.r,self.e)
if __name__=="__main__": unittest.main()
