import unittest
from pydantic import ValidationError
from app.observability.llm_profiler_step445.engine import LLMCallSample,ProfileRequest,profile_llm_usage
class Step445Tests(unittest.TestCase):
    def test_aggregation(self):
        s=[LLMCallSample(model_name='m',latency_ms=100,tokens_prompt=10,tokens_completion=5),LLMCallSample(model_name='m',latency_ms=200,tokens_prompt=20,tokens_completion=5,success=False)]
        p=profile_llm_usage(ProfileRequest(window_id='w',samples=s)).models[0]
        self.assertEqual(p.calls,2)
        self.assertEqual(p.success_rate,.5)
        self.assertEqual(p.tuning_hint,'degrade')
    def test_empty(self):
        self.assertEqual(profile_llm_usage(ProfileRequest(window_id='w',samples=[])).models,[])
    def test_nonfinite(self):
        with self.assertRaises(ValidationError):LLMCallSample(model_name='m',latency_ms=float('inf'),tokens_prompt=0,tokens_completion=0)
    def test_nan(self):
        with self.assertRaises(ValidationError):LLMCallSample(model_name='m',latency_ms=float('nan'),tokens_prompt=0,tokens_completion=0)
    def test_token_bound(self):
        with self.assertRaises(ValidationError):LLMCallSample(model_name='m',latency_ms=1,tokens_prompt=1000000001,tokens_completion=0)
    def test_utc(self):
        self.assertTrue(profile_llm_usage(ProfileRequest(window_id='w',samples=[])).meta['created_at'].endswith('Z'))
