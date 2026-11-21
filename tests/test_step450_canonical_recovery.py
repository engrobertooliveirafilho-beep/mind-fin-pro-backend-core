import unittest
from fastapi import HTTPException
from pydantic import ValidationError
from app.cognition.distributed_agents_step450.engine import ClusterConfig,DistributedAgentConfig,DistributedRequest,run_distributed_agents
def req(clusters=None,agents=None,fanout=2):
    return DistributedRequest(task='paper allocation',clusters=clusters if clusters is not None else [ClusterConfig(cluster_id='c1',capacity=10,latency_ms=1)],agents=agents if agents is not None else [DistributedAgentConfig(agent_id='a1',role='planner')],fanout=fanout)
class Step450Tests(unittest.TestCase):
    def test_assignments(self):
        self.assertEqual(len(run_distributed_agents(req()).assignments),2)
    def test_max_fanout(self):
        self.assertEqual(len(run_distributed_agents(req(fanout=10)).assignments),10)
    def test_duplicate_cluster(self):
        c=ClusterConfig(cluster_id='c',capacity=1,latency_ms=0)
        with self.assertRaises(HTTPException) as x:run_distributed_agents(req(clusters=[c,c]))
        self.assertEqual(x.exception.status_code,422)
    def test_duplicate_agent(self):
        a=DistributedAgentConfig(agent_id='a',role='planner')
        with self.assertRaises(HTTPException):run_distributed_agents(req(agents=[a,a]))
    def test_empty_clusters(self):
        with self.assertRaises(ValidationError):req(clusters=[])
    def test_nonfinite_latency(self):
        with self.assertRaises(HTTPException):run_distributed_agents(req(clusters=[ClusterConfig(cluster_id='c',capacity=1,latency_ms=float('inf'))]))
    def test_utc(self):
        self.assertTrue(run_distributed_agents(req()).meta['created_at'].endswith('Z'))
