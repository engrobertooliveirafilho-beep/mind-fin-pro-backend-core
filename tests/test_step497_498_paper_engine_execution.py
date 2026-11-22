import unittest
from app.runtime.step497_498_mock_guard import (
    execute_paper_pipeline, execute_paper_briefing, MockDataBlocked
)
from recovered.finance_steps.step497_pipeline_engine_original import get_business_pipeline_snapshot

class PaperEngineExecution(unittest.TestCase):
    def test_original_497_executes_but_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked, 'HISTORICAL_MOCK_DATA'):
            execute_paper_pipeline(get_business_pipeline_snapshot)
    def test_original_497_metadata(self):
        payload=get_business_pipeline_snapshot()
        self.assertEqual(payload['version'],'step497-v1')
        self.assertEqual(payload['metrics']['estimated_monthly_recurring_revenue_usd'],18000)
    def test_original_497_pipeline_not_authorized(self):
        with self.assertRaises(MockDataBlocked):
            execute_paper_pipeline(lambda: {'version':'step497-v1','status':'ok'})
    def test_498_mock_contamination_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked,'MOCK_CONTAMINATED_BRIEFING'):
            execute_paper_briefing(lambda: {'version':'step498-v1','pipeline':get_business_pipeline_snapshot()})
    def test_498_missing_dependency_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked,'INCOMPLETE_DEPENDENCIES'):
            execute_paper_briefing(lambda: {'version':'step498-v1'})
    def test_unknown_pipeline_blocked(self):
        with self.assertRaises(MockDataBlocked):
            execute_paper_pipeline(lambda: {'version':'step497-v2'})
    def test_no_engine_denied(self):
        with self.assertRaises(ValueError): execute_paper_pipeline(None)
    def test_no_ceo_engine_denied(self):
        with self.assertRaises(ValueError): execute_paper_briefing(None)
