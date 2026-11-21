import unittest
from pydantic import ValidationError
from app.cognition.parallel_reasoning_step451.engine import ParallelReasoningRequest,BranchConfig,run_parallel_reasoning
class Step451Tests(unittest.TestCase):
    def test_default(self):
        r=run_parallel_reasoning(ParallelReasoningRequest(topic='risk'))
        self.assertEqual((len(r.branches),len(r.branches[0].steps)),(3,3))
    def test_max_branches(self):
        r=run_parallel_reasoning(ParallelReasoningRequest(topic='risk',config=BranchConfig(branches=12,depth=8)))
        self.assertEqual(sum(len(b.steps) for b in r.branches),96)
    def test_topic_limit(self):
        with self.assertRaises(ValidationError):ParallelReasoningRequest(topic='x'*4097)
    def test_empty_topic(self):
        with self.assertRaises(ValidationError):ParallelReasoningRequest(topic='')
    def test_invalid_branches(self):
        with self.assertRaises(ValidationError):BranchConfig(branches=13)
    def test_utc(self):
        r=run_parallel_reasoning(ParallelReasoningRequest(topic='risk'))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
