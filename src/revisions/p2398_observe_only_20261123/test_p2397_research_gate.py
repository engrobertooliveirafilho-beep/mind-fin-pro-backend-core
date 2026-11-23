import unittest
from p2397_research_gate import evaluate_research
EDGE={'decision':'OBSERVE_SCORE','key':'A|B|C|D','real_execution_allowed':False,'paper_stack_modified':False}
POLICY={'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','runtime_modification_allowed':False,'broker_execution_allowed':False,'ftmo_real_allowed':False,'learning_scope':'OFFLINE_RESEARCH_ONLY','next_research_biases':['a','b','c']}
TYPES=['DD_REDUCTION','SESSION_FOOTPRINT_PRIORITY','CYCLE_TRANSITION_EXPANSION']
ROWS=[{'type':t,'hypothesis_id':f'P2397_HYP_{i}','paper_only':True,'base_context':EDGE['key'],'recommended_search_bias':POLICY['next_research_biases'][i]} for i,t in enumerate(TYPES)]
class ResearchTests(unittest.TestCase):
    def test_observation_only(self):
        r=evaluate_research(EDGE,POLICY,ROWS)
        self.assertEqual(r.decision,'RESEARCH_ONLY')
        self.assertFalse(r.allowed_for_runtime)
    def test_promoted_blocked(self):
        self.assertEqual(evaluate_research({**EDGE,'decision':'PROMOTE_SCORE'},POLICY,ROWS).decision,'BLOCK')
    def test_runtime_policy_blocked(self):
        self.assertEqual(evaluate_research(EDGE,{**POLICY,'runtime_modification_allowed':True},ROWS).decision,'BLOCK')
    def test_duplicate_hypothesis_blocked(self):
        self.assertEqual(evaluate_research(EDGE,POLICY,[ROWS[0],ROWS[0],ROWS[2]]).decision,'BLOCK')
    def test_wrong_context_blocked(self):
        self.assertEqual(evaluate_research(EDGE,POLICY,[{**ROWS[0],'base_context':'X'},*ROWS[1:]]).decision,'BLOCK')
    def test_missing_hypotheses_blocked(self):
        self.assertEqual(evaluate_research(EDGE,POLICY,ROWS[:2]).decision,'BLOCK')
if __name__=='__main__': unittest.main()
