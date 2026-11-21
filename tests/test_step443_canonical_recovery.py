import unittest
from fastapi import HTTPException
from pydantic import ValidationError
from app.infra.rate_limit_step443.engine import ModelUsage,RateLimitRequest,evaluate_rate_limits
def usage(name='m',**kw):
    return ModelUsage(model_name=name,rpm_current=kw.get('rpm',100),tpm_current=kw.get('tpm',1000),error_rate=kw.get('error',0),latency_ms_avg=kw.get('latency',100))
class Step443Tests(unittest.TestCase):
    def test_balanced(self):
        r=evaluate_rate_limits(RateLimitRequest(models=[usage()]))
        self.assertEqual(r.decisions[0].rpm_limit,100)
    def test_conservative(self):
        r=evaluate_rate_limits(RateLimitRequest(policy='conservative',models=[usage()]))
        self.assertEqual(r.decisions[0].rpm_limit,70)
    def test_throttle_on_errors(self):
        r=evaluate_rate_limits(RateLimitRequest(models=[usage(error=.5)]))
        self.assertEqual(r.decisions[0].status,'throttle')
    def test_duplicate_rejected(self):
        with self.assertRaises(HTTPException) as e:evaluate_rate_limits(RateLimitRequest(models=[usage(),usage()]))
        self.assertEqual(e.exception.status_code,422)
    def test_nan_rejected(self):
        with self.assertRaises(ValidationError):usage(error=float('nan'))
    def test_inf_rejected(self):
        with self.assertRaises(ValidationError):usage(latency=float('inf'))
    def test_utc(self):
        self.assertTrue(evaluate_rate_limits(RateLimitRequest(models=[])).meta['created_at'].endswith('Z'))
    def test_zero_usage_does_not_invent_quota(self):
        r=evaluate_rate_limits(RateLimitRequest(models=[usage(rpm=0,tpm=0)]))
        self.assertEqual(r.decisions[0].rpm_limit,0)
        self.assertEqual(r.decisions[0].tpm_limit,0)
    def test_zero_rpm_independent_of_tpm(self):
        r=evaluate_rate_limits(RateLimitRequest(models=[usage(rpm=0,tpm=100)]))
        self.assertEqual(r.decisions[0].rpm_limit,0)
        self.assertEqual(r.decisions[0].tpm_limit,100)
    def test_zero_quota_throttles_even_under_aggressive_policy(self):
        r=evaluate_rate_limits(RateLimitRequest(policy='aggressive',models=[usage(rpm=0,tpm=100)]))
        self.assertEqual(r.decisions[0].status,'throttle')
