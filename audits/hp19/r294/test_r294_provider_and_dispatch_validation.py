import math
import unittest
from safe_dispatch_allocator import allocate_shards, DispatchRejected
from research_provider_gate import run_research, ResearchUnavailable

class R294Tests(unittest.TestCase):
    def setUp(self):
        self.clusters=[{"cluster_id":"a","capacity":2,"latency_ms":10},{"cluster_id":"b","capacity":2,"latency_ms":20}]
        self.agents=[{"agent_id":"x","role":"researcher"},{"agent_id":"y","role":"planner"}]
    def test_allocator_is_deterministic_and_capacity_bounded(self):
        first=allocate_shards(self.clusters,self.agents,2)
        self.assertEqual(first,allocate_shards(self.clusters,self.agents,2))
        self.assertEqual(len(first),4)
        self.assertTrue(all(sum(x['cluster_id']==c['cluster_id'] for x in first)<=c['capacity'] for c in self.clusters))
    def test_nonfinite_latency_rejected(self):
        bad=[dict(self.clusters[0],latency_ms=float('nan')),self.clusters[1]]
        with self.assertRaisesRegex(DispatchRejected,'INVALID_LATENCY'): allocate_shards(bad,self.agents)
    def test_boolean_weight_rejected(self):
        bad=[dict(self.agents[0],weight=True),self.agents[1]]
        with self.assertRaisesRegex(DispatchRejected,'INVALID_WEIGHT'): allocate_shards(self.clusters,bad)
    def test_unknown_role_rejected(self):
        bad=[dict(self.agents[0],role='root'),self.agents[1]]
        with self.assertRaisesRegex(DispatchRejected,'INVALID_ROLE'): allocate_shards(self.clusters,bad)
    def test_insufficient_capacity_rejected(self):
        with self.assertRaisesRegex(DispatchRejected,'INSUFFICIENT_CAPACITY'): allocate_shards(self.clusters,self.agents,3)
    def test_research_requires_provider(self):
        with self.assertRaises(ResearchUnavailable): run_research('test','hybrid')
    def test_research_rejects_stub_urls(self):
        p=lambda **kw:[{'title':'x','snippet':'y','source':'stub://research/1'}]
        with self.assertRaisesRegex(ResearchUnavailable,'HTTPS'): run_research('test','web_stub',p)
    def test_research_rejects_missing_provenance(self):
        p=lambda **kw:[{'title':'x','snippet':'y'}]
        with self.assertRaisesRegex(ResearchUnavailable,'missing'): run_research('test','internal',p)
    def test_research_rejects_provider_failure(self):
        def p(**kw): raise RuntimeError('offline')
        with self.assertRaises(ResearchUnavailable): run_research('test','hybrid',p)
    def test_research_accepts_https_source(self):
        p=lambda **kw:[{'title':'title','snippet':'summary','source':'https://example.org/article'}]
        out=run_research('test','hybrid',p)
        self.assertEqual(out[0]['source'],'https://example.org/article')
    def test_empty_query_rejected(self):
        p=lambda **kw:[]
        with self.assertRaisesRegex(ValueError,'EMPTY_RESEARCH_QUERY'): run_research(' ','hybrid',p)

if __name__=='__main__': unittest.main()
