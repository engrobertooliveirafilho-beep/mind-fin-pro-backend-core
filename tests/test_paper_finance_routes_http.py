import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.runtime.paper_finance_routes import router

class PaperFinanceHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app=FastAPI()
        app.include_router(router)
        cls.client=TestClient(app,raise_server_exceptions=True)
    def test_pipeline_returns_503(self):
        self.assertEqual(self.client.get('/paper/finance/pipeline').status_code,503)
    def test_pipeline_no_mock_metrics_leaked(self):
        self.assertNotIn('18000',self.client.get('/paper/finance/pipeline').text)
    def test_pipeline_explicit_error(self):
        self.assertEqual(self.client.get('/paper/finance/pipeline').json()['detail'],'PAPER_PIPELINE_NOT_CERTIFIED')
    def test_ceo_returns_503(self):
        self.assertEqual(self.client.get('/paper/finance/ceo-briefing').status_code,503)
    def test_ceo_explicit_error(self):
        self.assertEqual(self.client.get('/paper/finance/ceo-briefing').json()['detail'],'PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED')
    def test_ceo_does_not_leak_mock_metrics(self):
        self.assertNotIn('60000',self.client.get('/paper/finance/ceo-briefing').text)
    def test_no_real_trade_route(self):
        self.assertEqual(self.client.post('/paper/finance/order',json={}).status_code,404)
    def test_original_unprotected_route_not_mounted(self):
        self.assertEqual(self.client.get('/biz/pipeline/snapshot').status_code,404)

    def test_router_does_not_import_original_mock_engine(self):
        import inspect
        from app.runtime import paper_finance_routes
        source=inspect.getsource(paper_finance_routes)
        self.assertNotIn('from recovered.finance_steps',source)
        self.assertNotIn('import recovered.finance_steps',source)
