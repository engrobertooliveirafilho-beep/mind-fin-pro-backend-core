import unittest
from r851_unified_dispatch import dispatch, ALLOWED

def good(_): return {'status': 'planned', 'plans': [{'step_id': 10}]}
def reg(agent='dev.step_planner_agent', handler=good):
    return {agent: (handler, {'agent_id': agent, 'reviewed': True,
                             'offline_only': True, 'source_attested': True})}
A = 'dev.step_planner_agent'
class Tests(unittest.TestCase):
    def test_known(self): self.assertEqual(len(ALLOWED), 5)
    def test_unknown(self): self.assertEqual(dispatch('unknown')['reason'], 'unknown_agent')
    def test_unhashable(self): self.assertEqual(dispatch([])['status'], 'blocked')
    def test_none(self): self.assertEqual(dispatch(None)['status'], 'blocked')
    def test_no_registry(self): self.assertEqual(dispatch(A)['reason'], 'no_reviewed_registry')
    def test_empty_registry(self): self.assertEqual(dispatch(A, registry={})['reason'], 'missing_reviewed_handler')
    def test_wrong_handler(self): self.assertEqual(dispatch(A, registry={A: None})['status'], 'blocked')
    def test_valid(self): self.assertEqual(dispatch(A, registry=reg())['status'], 'planned')
    def test_plan(self): self.assertEqual(dispatch(A, registry=reg())['plan'][0]['step_id'], 10)
    def test_no_runtime(self): self.assertFalse(dispatch(A, registry=reg())['runtime_certified'])
    def test_no_integration(self): self.assertFalse(dispatch(A, registry=reg())['integration_authorized'])
    def test_invalid_payload(self): self.assertEqual(dispatch(A, [], registry=reg())['reason'], 'invalid_payload')
    def test_wrong_agent_binding(self): self.assertEqual(dispatch(A, registry=reg('dev.test_guardian_agent'))['status'], 'blocked')
    def test_untrusted_evidence(self): self.assertEqual(dispatch(A, registry={A: (good, {'reviewed': True})})['status'], 'blocked')
    def test_noncallable(self): self.assertEqual(dispatch(A, registry=reg(handler='bad'))['status'], 'blocked')
    def test_exception(self):
        def fail(_): raise RuntimeError('secret')
        self.assertEqual(dispatch(A, registry=reg(handler=fail))['reason'], 'handler_failed')
    def test_no_error_leak(self):
        def fail(_): raise RuntimeError('secret')
        self.assertNotIn('secret', str(dispatch(A, registry=reg(handler=fail))))
    def test_bad_result(self): self.assertEqual(dispatch(A, registry=reg(handler=lambda _: None))['reason'], 'handler_rejected')
    def test_stub_result(self): self.assertEqual(dispatch(A, registry=reg(handler=lambda _: {'status': 'not_implemented'}))['status'], 'blocked')
    def test_all_agent_ids(self):
        for agent in ALLOWED:
            self.assertEqual(dispatch(agent, registry=reg(agent))['status'], 'planned')
if __name__ == '__main__': unittest.main()
