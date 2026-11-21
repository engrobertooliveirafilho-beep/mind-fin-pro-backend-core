import unittest
from step455_index import VectorIndex, IndexErrorSafety

class Tests(unittest.TestCase):
    def setUp(self):
        self.idx=VectorIndex(8,'paper')
        self.a=[1,0,0,0,0,0,0,0]
        self.b=[0,1,0,0,0,0,0,0]
    def test_add_search(self):
        self.idx.add('a',self.a)
        self.assertEqual(self.idx.search(self.a)[0]['source_id'],'a')
    def test_rank(self):
        self.idx.add('a',self.a);self.idx.add('b',self.b)
        self.assertEqual(self.idx.search(self.b)[0]['source_id'],'b')
    def test_empty(self):self.assertEqual(self.idx.search(self.a),[])
    def test_dimension(self):
        with self.assertRaises(IndexErrorSafety):self.idx.add('a',[1])
    def test_nonfinite(self):
        with self.assertRaises(IndexErrorSafety):self.idx.add('a',[float('nan')]+[0]*7)
    def test_zero(self):
        with self.assertRaises(IndexErrorSafety):self.idx.add('a',[0]*8)
    def test_duplicate(self):
        self.idx.add('a',self.a)
        with self.assertRaises(IndexErrorSafety):self.idx.add('a',self.b)
    def test_limit(self):
        with self.assertRaises(IndexErrorSafety):self.idx.search(self.a,0)
    def test_namespace(self):
        self.idx.add('a',self.a)
        self.assertEqual(self.idx.search(self.a)[0]['namespace'],'paper')
    def test_determinism(self):
        self.idx.add('a',self.a)
        self.assertEqual(self.idx.search(self.a),self.idx.search(self.a))
    def test_boolean(self):
        with self.assertRaises(IndexErrorSafety):self.idx.add('a',[True]+[0]*7)
    def test_invalid_id(self):
        with self.assertRaises(IndexErrorSafety):self.idx.add('',self.a)

if __name__=='__main__':unittest.main()
