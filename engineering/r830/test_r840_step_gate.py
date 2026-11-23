import unittest
from r840_step_gate import classify, validate
E={'id':'s1','path_canonical':'steps/step1.py','status':'CANDIDATE','source_bucket_prefix':'COGNITIVE'}
class TestR840(unittest.TestCase):
 def test_candidate(self): self.assertEqual(classify('steps/step1.py'),'COGNITIVE_CANDIDATE')
 def test_nested(self): self.assertEqual(classify('archive/steps/step123.json'),'COGNITIVE_CANDIDATE')
 def test_nonstep(self): self.assertEqual(classify('docs/guide.md'),'UNCLASSIFIED')
 def test_backslash(self): self.assertEqual(classify('a\\steps\\step1.py'),'COGNITIVE_CANDIDATE')
 def test_traversal(self): self.assertEqual(classify('../steps/step1.py'),'INVALID')
 def test_absolute(self): self.assertEqual(classify('/steps/step1.py'),'INVALID')
 def test_drive(self): self.assertEqual(classify('C:\\steps\\step1.py'),'INVALID')
 def test_nul(self): self.assertEqual(classify('steps/step\x001.py'),'INVALID')
 def test_empty(self): self.assertFalse(validate([])['valid'])
 def test_candidate_registry(self): self.assertTrue(validate([E])['valid'])
 def test_duplicate(self): self.assertFalse(validate([E,E])['valid'])
 def test_bad_status(self): self.assertFalse(validate([dict(E,status='CERTIFIED')])['valid'])
 def test_unverified(self): self.assertFalse(validate([dict(E,status='VERIFIED_SOURCE')])['valid'])
 def test_hash(self): self.assertTrue(validate([dict(E,status='VERIFIED_SOURCE')],{'steps/step1.py':'a'*64})['valid'])
 def test_never_certifies(self): self.assertFalse(validate([E])['certified'])
 def test_schema(self): self.assertFalse(validate([{'id':'x'}])['valid'])
if __name__=='__main__': unittest.main()
