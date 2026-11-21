import unittest
from step452_retrieval import search, RetrievalError

DOCS = [{'source_id':'drive:1','title':'Risk engine','text':'risk limits for paper trading'}, {'source_id':'drive:2','title':'Other','text':'historical archive'}]
class Tests(unittest.TestCase):
    def test_real_hit(self): self.assertEqual(search('risk', DOCS)[0]['source_id'],'drive:1')
    def test_no_fabrication(self): self.assertEqual(search('absentword', DOCS),[])
    def test_no_documents(self): self.assertEqual(search('risk',[]),[])
    def test_limit(self): self.assertEqual(len(search('risk',DOCS,1)),1)
    def test_empty_query(self):
        with self.assertRaises(RetrievalError): search(' ',DOCS)
    def test_missing_provenance(self):
        with self.assertRaises(RetrievalError): search('risk',[{'title':'x','text':'risk'}])
    def test_duplicate(self):
        with self.assertRaises(RetrievalError): search('risk',DOCS+[DOCS[0]])
    def test_bad_limit(self):
        with self.assertRaises(RetrievalError): search('risk',DOCS,True)
    def test_determinism(self): self.assertEqual(search('risk',DOCS),search('risk',DOCS))
if __name__=='__main__': unittest.main()
