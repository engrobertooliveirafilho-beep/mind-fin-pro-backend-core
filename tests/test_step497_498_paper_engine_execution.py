import unittest
from app.runtime.step497_498_mock_guard import (
    execute_paper_pipeline, execute_paper_briefing, MockDataBlocked
)
from recovered.finance_steps.step497_pipeline_engine_original import get_business_pipeline_snapshot

class PaperEngineExecution(unittest.TestCase):
    def test_original_497_executes_but_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked, 'PAPER_PIPELINE_NOT_CERTIFIED'):
            execute_paper_pipeline(get_business_pipeline_snapshot)
    def test_original_provenance_denied_before_invocation(self):
        calls=[]
        def get_business_pipeline_snapshot():
            calls.append('executed')
            return {'version':'step497-v1'}
        get_business_pipeline_snapshot.__module__='recovered.finance_steps.step497_pipeline_engine_original'
        with self.assertRaisesRegex(MockDataBlocked,'PAPER_PIPELINE_NOT_CERTIFIED'):
            execute_paper_pipeline(get_business_pipeline_snapshot)
        self.assertEqual(calls,[])
    def test_original_497_metadata(self):
        payload=get_business_pipeline_snapshot()
        self.assertEqual(payload['version'],'step497-v1')
        self.assertEqual(payload['metrics']['estimated_monthly_recurring_revenue_usd'],18000)
    def test_original_497_pipeline_not_authorized(self):
        with self.assertRaises(MockDataBlocked):
            execute_paper_pipeline(lambda: {'version':'step497-v1','status':'ok'})
    def test_498_mock_contamination_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked,'PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED'):
            execute_paper_briefing(lambda: {'version':'step498-v1','pipeline':get_business_pipeline_snapshot()})
    def test_original_498_denied_before_invocation(self):
        calls=[]
        def build_ceo_briefing():
            calls.append('executed')
            return {'version':'step498-v1','pipeline':{'version':'step497-v1'}}
        build_ceo_briefing.__module__='recovered.finance_steps.step498_ceo_engine_original'
        with self.assertRaisesRegex(MockDataBlocked,'PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED'):
            execute_paper_briefing(build_ceo_briefing)
        self.assertEqual(calls,[])
    def test_498_missing_dependency_blocked(self):
        with self.assertRaisesRegex(MockDataBlocked,'PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED'):
            execute_paper_briefing(lambda: {'version':'step498-v1'})
    def test_unknown_pipeline_blocked(self):
        with self.assertRaises(MockDataBlocked):
            execute_paper_pipeline(lambda: {'version':'step497-v2'})
    def test_no_engine_denied(self):
        with self.assertRaises(ValueError): execute_paper_pipeline(None)
    def test_no_ceo_engine_denied(self):
        with self.assertRaises(ValueError): execute_paper_briefing(None)

    def test_unknown_pipeline_does_not_execute(self):
        calls=[]
        def engine():
            calls.append(True)
            return {'version':'other'}
        with self.assertRaises(MockDataBlocked):
            execute_paper_pipeline(engine)
        self.assertEqual(calls,[])
    def test_unknown_ceo_does_not_execute(self):
        calls=[]
        def engine():
            calls.append(True)
            return {'version':'other'}
        with self.assertRaises(MockDataBlocked):
            execute_paper_briefing(engine)
        self.assertEqual(calls,[])
