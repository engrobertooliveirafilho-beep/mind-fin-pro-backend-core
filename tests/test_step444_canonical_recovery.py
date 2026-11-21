import unittest
from pydantic import ValidationError
from fastapi import HTTPException
from app.cognition.context_cost_step444.engine import ContextSegment,BalanceRequest,balance_context
class Step444Tests(unittest.TestCase):
    def test_full_fit(self):
        r=balance_context(BalanceRequest(segments=[ContextSegment(segment_id='a',tokens=100,priority=5,cost_per_1k=1)],max_tokens=100,max_cost=1))
        self.assertEqual(r.totals['total_tokens'],100)
    def test_partial(self):
        r=balance_context(BalanceRequest(segments=[ContextSegment(segment_id='a',tokens=100,priority=5,cost_per_1k=1)],max_tokens=50,max_cost=1))
        self.assertEqual(r.allocations[0].status,'partial')
    def test_infinite_cost_rejected(self):
        with self.assertRaises(ValidationError):BalanceRequest(segments=[],max_tokens=100,max_cost=float('inf'))
    def test_nan_unit_price_rejected(self):
        with self.assertRaises(ValidationError):ContextSegment(segment_id='a',tokens=1,priority=1,cost_per_1k=float('nan'))
    def test_utc(self):
        r=balance_context(BalanceRequest(segments=[],max_tokens=100,max_cost=1))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
    def test_duplicate_segment_id(self):
        p=ContextSegment(segment_id='same',tokens=1,priority=1,cost_per_1k=1)
        with self.assertRaises(HTTPException) as e:
            balance_context(BalanceRequest(segments=[p,p.model_copy()],max_tokens=100,max_cost=1))
        self.assertEqual(e.exception.status_code,422)
    def test_cost_budget_never_exceeded(self):
        p=ContextSegment(segment_id='x',tokens=100000,priority=1,cost_per_1k=.3)
        r=balance_context(BalanceRequest(segments=[p],max_tokens=100000,max_cost=.1))
        self.assertLessEqual(r.allocations[0].included_tokens*.3/1000,.1)
