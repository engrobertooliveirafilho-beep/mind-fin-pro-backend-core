import unittest
from pydantic import ValidationError
from app.embeddings.internal_embeddings_step454.engine import EmbedRequest,embed_internal
class Step454Tests(unittest.TestCase):
    def test_deterministic(self):
        a=embed_internal(EmbedRequest(text='abc'))
        b=embed_internal(EmbedRequest(text='abc'))
        self.assertEqual(a.vector,b.vector)
    def test_dim(self):
        r=embed_internal(EmbedRequest(text='abc',dim=256))
        self.assertEqual(len(r.vector),256)
    def test_checksum_namespace(self):
        a=embed_internal(EmbedRequest(text='abc',namespace='a'))
        b=embed_internal(EmbedRequest(text='abc',namespace='b'))
        self.assertNotEqual(a.checksum,b.checksum)
    def test_text_limit(self):
        with self.assertRaises(ValidationError):EmbedRequest(text='x'*65537)
    def test_namespace_limit(self):
        with self.assertRaises(ValidationError):EmbedRequest(text='x',namespace='n'*129)
    def test_invalid_dim(self):
        with self.assertRaises(ValidationError):EmbedRequest(text='x',dim=7)
