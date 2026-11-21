import math
import unittest
from step454_embeddings import embed, EmbeddingError

class TestEmbeddings(unittest.TestCase):
    def test_dim(self): self.assertEqual(len(embed('alpha')['vector']),32)
    def test_deterministic(self): self.assertEqual(embed('alpha'),embed('alpha'))
    def test_namespace_isolated(self): self.assertNotEqual(embed('alpha',namespace='x')['checksum'],embed('alpha',namespace='y')['checksum'])
    def test_order_invariant_vector(self): self.assertEqual(embed('alpha beta')['vector'],embed('beta alpha')['vector'])
    def test_case_insensitive_vector(self): self.assertEqual(embed('ALPHA')['vector'],embed('alpha')['vector'])
    def test_normalized(self): self.assertAlmostEqual(math.sqrt(sum(x*x for x in embed('alpha beta')['vector'])),1)
    def test_empty(self):
        with self.assertRaises(EmbeddingError): embed(' ')
    def test_invalid_dim(self):
        with self.assertRaises(EmbeddingError): embed('alpha',dim=1)
    def test_boolean_dim(self):
        with self.assertRaises(EmbeddingError): embed('alpha',dim=True)
    def test_namespace(self):
        with self.assertRaises(EmbeddingError): embed('alpha',namespace='')
    def test_no_semantic_claim(self): self.assertFalse(embed('alpha')['semantic_model'])
    def test_checksum_changes(self): self.assertNotEqual(embed('alpha')['checksum'],embed('beta')['checksum'])
if __name__ == '__main__': unittest.main()
