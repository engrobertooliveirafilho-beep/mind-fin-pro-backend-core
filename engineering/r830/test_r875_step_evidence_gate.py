import unittest
from r875_step_evidence_gate import classify

class TestEvidenceGate(unittest.TestCase):
    def test_title(self): self.assertEqual(classify(464,[464],{'464':'Marketing'}, {})['status'],'definition_recovered')
    def test_missing_title(self): self.assertEqual(classify(520,[520],{}, {})['status'],'identifier_only')
    def test_not_in_registry(self): self.assertEqual(classify(464,[],{'464':'Marketing'}, {})['status'],'blocked')
    def test_bool_id(self): self.assertEqual(classify(True,[1],{}, {})['status'],'blocked')
    def test_bad_registry(self): self.assertEqual(classify(1,[True],{}, {})['status'],'blocked')
    def test_bad_titles(self): self.assertEqual(classify(1,[1],None, {})['status'],'blocked')
    def test_bad_evidence(self): self.assertEqual(classify(1,[1],{}, None)['status'],'blocked')
    def test_bad_digest(self): self.assertEqual(classify(464,[464],{'464':'Marketing'},{'sha256':'abc'})['status'],'blocked')
    def test_good_format_not_certified(self): self.assertFalse(classify(464,[464],{'464':'Marketing'},{'sha256':'a'*64})['certified'])
    def test_no_execution(self): self.assertFalse(classify(464,[464],{'464':'Marketing'}, {})['execution_authorized'])
    def test_unverified_digest(self): self.assertTrue(classify(464,[464],{'464':'Marketing'},{'sha256':'a'*64})['has_unverified_digest'])
    def test_no_digest(self): self.assertFalse(classify(464,[464],{'464':'Marketing'}, {})['has_unverified_digest'])
    def test_blank_title(self): self.assertEqual(classify(464,[464],{'464':' '}, {})['status'],'identifier_only')
    def test_deterministic(self): self.assertEqual(classify(464,[464],{'464':'Marketing'}, {}),classify(464,[464],{'464':'Marketing'}, {}))

if __name__=='__main__': unittest.main()
