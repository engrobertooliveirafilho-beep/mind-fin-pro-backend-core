"""Offline regression against STEP457's historical decision algorithm.
The original decision engine was recovered from Drive; no FastAPI E2E claim.
"""
import unittest
from step457_integration import guarded_decision, PolicyViolation

def original_decision(*,queue_length,avg_latency_ms,current_instances,min_instances=0,max_instances=64,target_latency_ms=1500.,cost_sensitivity=1.):
    q=max(0,int(queue_length));cur=max(0,int(current_instances));minimum=max(0,int(min_instances));maximum=max(minimum+1,int(max_instances))
    cur=max(minimum,min(maximum,cur))
    latency=max(1.,float(avg_latency_ms));target=max(1.,float(target_latency_ms));sensitivity=max(.1,float(cost_sensitivity))
    pressure=q/10*.6+latency/target*.4;desired=cur
    if pressure>2:desired=min(maximum,cur+max(1,int(1+pressure/sensitivity)))
    elif pressure<.7 and q==0 and latency<target*.8:desired=max(minimum,cur-(1 if sensitivity<=1 else 0))
    return {'desired_instances':desired,'current_instances':cur}

class Tests(unittest.TestCase):
    def invoke(self,**kw):
        data=dict(queue_length=100,avg_latency_ms=3000,current_instances=1,min_instances=0,max_instances=8)
        data.update(kw)
        return guarded_decision(original_decision,**data)
    def test_blocks_up(self):self.assertTrue(self.invoke()['blocked_scale_out'])
    def test_no_execution(self):self.assertFalse(self.invoke()['authorized_to_execute'])
    def test_noop(self):self.assertEqual(self.invoke()['action'],'NO_OP')
    def test_unchanged(self):self.assertEqual(self.invoke()['authorized_instances'],1)
    def test_low(self):self.assertFalse(self.invoke(queue_length=0,avg_latency_ms=10)['blocked_scale_out'])
    def test_nan(self):
        with self.assertRaises(PolicyViolation):self.invoke(avg_latency_ms=float('nan'))
    def test_inf(self):
        with self.assertRaises(PolicyViolation):self.invoke(cost_sensitivity=float('inf'))
    def test_limits(self):
        with self.assertRaises(PolicyViolation):self.invoke(min_instances=3)
    def test_budget(self):
        with self.assertRaises(PolicyViolation):self.invoke(cost_limit_brl=1)
    def test_bool(self):
        with self.assertRaises(PolicyViolation):self.invoke(queue_length=True)
if __name__=='__main__':unittest.main()
