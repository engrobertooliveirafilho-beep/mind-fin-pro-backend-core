import unittest
from fastapi import HTTPException
from app.cognition.math_advanced_step453.engine import MathRequest,FinancePayload,AlgebraPayload,ProofPayload,solve_math
class Step453Tests(unittest.TestCase):
    def test_npv(self):
        r=solve_math(MathRequest(mode='finance',finance=FinancePayload(rate=.1,cashflows=[-100,110])))
        self.assertEqual(r.result['npv'],0)
    def test_algebra(self):
        r=solve_math(MathRequest(mode='algebra',algebra=AlgebraPayload(a=2,b=4)))
        self.assertEqual(r.result['x'],-2)
    def test_proof_outline_only(self):
        r=solve_math(MathRequest(mode='proof',proof=ProofPayload(statement='A implies B')))
        self.assertIn('outline',r.result)
    def test_missing_payload_422(self):
        with self.assertRaises(HTTPException) as c:solve_math(MathRequest(mode='finance'))
        self.assertEqual(c.exception.status_code,422)
    def test_nan_rejected(self):
        with self.assertRaises(HTTPException):solve_math(MathRequest(mode='finance',finance=FinancePayload(rate=float('nan'),cashflows=[1])))
    def test_inf_algebra_rejected(self):
        with self.assertRaises(HTTPException):solve_math(MathRequest(mode='algebra',algebra=AlgebraPayload(a=float('inf'),b=2)))
    def test_utc(self):
        r=solve_math(MathRequest(mode='proof',proof=ProofPayload(statement='A')))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
