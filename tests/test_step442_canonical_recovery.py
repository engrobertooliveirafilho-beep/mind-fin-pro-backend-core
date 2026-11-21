import unittest
from fastapi import HTTPException
from pydantic import ValidationError
from app.infra.replication_step442.engine import RegionConfig,ReplicationPlanRequest,plan_replication
def region(name='a',latency=10,capacity=100):
    return RegionConfig(name=name,base_latency_ms=latency,write_capacity_rps=capacity)
class Step442Tests(unittest.TestCase):
    def test_allocation(self):
        r=plan_replication(ReplicationPlanRequest(regions=[region(),region('b')],global_write_rate_rps=100))
        self.assertEqual(sum(x.assigned_write_rps for x in r.regions),100)
    def test_empty_rejected(self):
        with self.assertRaises(ValidationError):ReplicationPlanRequest(regions=[],global_write_rate_rps=10)
    def test_duplicate_rejected(self):
        with self.assertRaises(HTTPException):plan_replication(ReplicationPlanRequest(regions=[region(),region()],global_write_rate_rps=10))
    def test_infinite_rejected(self):
        with self.assertRaises(ValidationError):region(latency=float('inf'))
    def test_nan_rejected(self):
        with self.assertRaises(ValidationError):region(capacity=float('nan'))
    def test_utc(self):
        r=plan_replication(ReplicationPlanRequest(regions=[region()],global_write_rate_rps=10))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
