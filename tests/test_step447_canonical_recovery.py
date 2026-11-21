import unittest
from pydantic import ValidationError
from app.cognition.self_critique_step447.engine import SelfCritiqueRequest,run_self_critique
class Step447Tests(unittest.TestCase):
    def test_short_medium(self):
        r=run_self_critique(SelfCritiqueRequest(output='short',severity='low'))
        self.assertEqual(r.critique[0].severity,'medium')
    def test_short_high(self):
        r=run_self_critique(SelfCritiqueRequest(output='short',severity='high'))
        self.assertEqual(r.critique[0].severity,'high')
    def test_finance_risk(self):
        r=run_self_critique(SelfCritiqueRequest(output='this text does not mention financial risk',context='financas'))
        self.assertIn('no_risk',[i.code for i in r.critique])
    def test_empty_rejected(self):
        with self.assertRaises(ValidationError):SelfCritiqueRequest(output='')
    def test_utc(self):
        self.assertTrue(run_self_critique(SelfCritiqueRequest(output='ok')).meta['created_at'].endswith('Z'))
