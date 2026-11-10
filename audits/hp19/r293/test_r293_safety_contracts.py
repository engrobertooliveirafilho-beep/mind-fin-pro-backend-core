import unittest
from safe_dispatch_allocator import allocate_shards, DispatchRejected
from research_provider_gate import require_research_provider, ResearchUnavailable

class R293SafetyTests(unittest.TestCase):
    def setUp(self):
        self.clusters=[{"cluster_id":"a","capacity":2,"latency_ms":10},{"cluster_id":"b","capacity":2,"latency_ms":20}]
        self.agents=[{"agent_id":"x","role":"researcher"},{"agent_id":"y","role":"planner"}]
    def test_shards_respect_capacity(self):
        out=allocate_shards(self.clusters,self.agents,2)
        self.assertEqual(len(out),4)
        for c in self.clusters:
            self.assertLessEqual(sum(x["cluster_id"]==c["cluster_id"] for x in out),c["capacity"])
    def test_capacity_shortage_rejected(self):
        with self.assertRaisesRegex(DispatchRejected,"INSUFFICIENT_CAPACITY"):
            allocate_shards(self.clusters,self.agents,3)
    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(DispatchRejected,"DUPLICATE_CLUSTER_ID"):
            allocate_shards(self.clusters+[self.clusters[0]],self.agents)
        with self.assertRaisesRegex(DispatchRejected,"DUPLICATE_AGENT_ID"):
            allocate_shards(self.clusters,self.agents+[self.agents[0]])
    def test_invalid_fanout_rejected(self):
        with self.assertRaises(DispatchRejected): allocate_shards(self.clusters,self.agents,0)
    def test_research_without_provider_fails_closed(self):
        for mode in ("web_stub","internal","hybrid"):
            with self.assertRaises(ResearchUnavailable): require_research_provider(mode)
    def test_research_provider_contract(self):
        provider=lambda query: []
        self.assertIs(require_research_provider("hybrid",provider),provider)

if __name__ == "__main__": unittest.main()
