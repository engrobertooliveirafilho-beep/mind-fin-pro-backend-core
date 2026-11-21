import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.cognition.context_cost_step444.engine import router as context_router
from app.observability.llm_profiler_step445.engine import router as profiler_router

app=FastAPI()
app.include_router(context_router,prefix="/step444/context-cost")
app.include_router(profiler_router,prefix="/step445/llm-profiler")
client=TestClient(app)

class Step444445HttpIntegration(unittest.TestCase):
    def test_context_full_fit(self):
        r=client.post("/step444/context-cost/balance",json={"segments":[{"segment_id":"a","tokens":100,"priority":5,"cost_per_1k":1}],"max_tokens":100,"max_cost":1})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["totals"]["total_tokens"],100)
    def test_context_duplicate_rejected(self):
        s={"segment_id":"a","tokens":10,"priority":1,"cost_per_1k":1}
        r=client.post("/step444/context-cost/balance",json={"segments":[s,s],"max_tokens":100,"max_cost":1})
        self.assertEqual(r.status_code,422)
    def test_context_infinite_cost_rejected(self):
        r=client.post("/step444/context-cost/balance",json={"segments":[],"max_tokens":10,"max_cost":"Infinity"})
        self.assertEqual(r.status_code,422)
    def test_profiler_aggregate(self):
        r=client.post("/step445/llm-profiler/profile",json={"window_id":"w","samples":[{"model_name":"m","latency_ms":100,"tokens_prompt":5,"tokens_completion":5}]})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["models"][0]["calls"],1)
    def test_profiler_infinite_rejected(self):
        r=client.post("/step445/llm-profiler/profile",json={"window_id":"w","samples":[{"model_name":"m","latency_ms":"Infinity","tokens_prompt":1,"tokens_completion":1}]})
        self.assertEqual(r.status_code,422)
    def test_profiler_too_many_samples(self):
        sample={"model_name":"m","latency_ms":1,"tokens_prompt":1,"tokens_completion":1}
        r=client.post("/step445/llm-profiler/profile",json={"window_id":"w","samples":[sample]*10001})
        self.assertEqual(r.status_code,422)
