import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.multimodal_executor_step456.engine import router

class Step456HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app=FastAPI()
        app.include_router(router,prefix='/multimodal')
        cls.client=TestClient(app)
    def test_http_success(self):
        r=self.client.post('/multimodal/execute',json={'session_id':'s','channels':[{'channel_id':'a','modality':'text','size_bytes':8}]})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['routes'][0]['estimated_tokens'],2)
    def test_http_duplicate_422(self):
        r=self.client.post('/multimodal/execute',json={'session_id':'s','channels':[{'channel_id':'a','modality':'text','size_bytes':8},{'channel_id':'a','modality':'audio','size_bytes':8}]})
        self.assertEqual(r.status_code,422)
    def test_http_invalid_modality_422(self):
        r=self.client.post('/multimodal/execute',json={'session_id':'s','channels':[{'channel_id':'a','modality':'live','size_bytes':8}]})
        self.assertEqual(r.status_code,422)
