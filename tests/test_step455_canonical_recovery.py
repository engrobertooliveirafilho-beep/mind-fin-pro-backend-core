"""STEP455 original planner: bounded, offline-only integration checks."""
import unittest
from app.step455_vector_index.engine import VectorIndexPlanRequest,plan_vector_index

class Step455Tests(unittest.TestCase):
    def test_one_shard(self):
        r=plan_vector_index(VectorIndexPlanRequest(total_vectors=100,dim=32))
        self.assertEqual(r.shards_count,1)
        self.assertEqual(r.layout['1'].vectors_in_shard,100)
    def test_multiple_shards(self):
        r=plan_vector_index(VectorIndexPlanRequest(total_vectors=105,dim=32,max_shard_size=50,page_size=20))
        self.assertEqual([x.vectors_in_shard for x in r.layout.values()],[50,50,5])
    def test_compression(self):
        a=plan_vector_index(VectorIndexPlanRequest(total_vectors=1000,dim=128,compression='none'))
        b=plan_vector_index(VectorIndexPlanRequest(total_vectors=1000,dim=128,compression='int8'))
        self.assertAlmostEqual(a.total_bytes_mb,4*b.total_bytes_mb,delta=.005)
    def test_no_vectors_rejected(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):VectorIndexPlanRequest(total_vectors=0)
if __name__=='__main__':unittest.main()
