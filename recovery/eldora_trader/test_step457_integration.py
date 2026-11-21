import unittest
from step457_integration import guarded_decision, PolicyViolation

def engine(**kw):
    return {'desired_instances': min(kw['max_instances'],kw['current_instances'] + (1 if kw['queue_length'] > 10 else 0))}

class IntegrationTests(unittest.TestCase):
    def args(self, **kwargs):
        d=dict(queue_length=20,avg_latency_ms=2000,current_instances=1,min_instances=0,max_instances=4)
        d.update(kwargs)
        return d
    def test_blocks_scale_out(self):
        r=guarded_decision(engine,**self.args())
        self.assertTrue(r['blocked_scale_out']);self.assertFalse(r['authorized_to_execute'])
    def test_keeps_capacity(self):
        self.assertEqual(guarded_decision(engine,**self.args())['authorized_instances'],1)
    def test_no_op(self):self.assertEqual(guarded_decision(engine,**self.args())['action'],'NO_OP')
    def test_zero_queue(self):self.assertFalse(guarded_decision(engine,**self.args(queue_length=0))['blocked_scale_out'])
    def test_negative_queue(self):
        with self.assertRaises(PolicyViolation):guarded_decision(engine,**self.args(queue_length=-1))
    def test_nan_latency(self):
        with self.assertRaises(PolicyViolation):guarded_decision(engine,**self.args(avg_latency_ms=float('nan')))
    def test_invalid_budget(self):
        with self.assertRaises(PolicyViolation):guarded_decision(engine,**self.args(cost_limit_brl=1))
    def test_boolean_budget(self):
        with self.assertRaises(PolicyViolation):guarded_decision(engine,**self.args(cost_limit_brl=True))
    def test_missing_engine(self):
        with self.assertRaises(PolicyViolation):guarded_decision(None,**self.args())
    def test_invalid_engine_response(self):
        with self.assertRaises(PolicyViolation):guarded_decision(lambda **kw: {'desired_instances':'2'},**self.args())
    def test_out_of_bounds(self):
        with self.assertRaises(PolicyViolation):guarded_decision(lambda **kw: {'desired_instances':99},**self.args())
    def test_invalid_min_max(self):
        with self.assertRaises(PolicyViolation):guarded_decision(engine,**self.args(min_instances=5))
    def test_no_side_effects(self):
        calls=[]
        def mock(**kw):calls.append(kw);return {'desired_instances':2}
        r=guarded_decision(mock,**self.args())
        self.assertEqual(len(calls),1);self.assertFalse(r['authorized_to_execute'])
if __name__=='__main__':unittest.main()
