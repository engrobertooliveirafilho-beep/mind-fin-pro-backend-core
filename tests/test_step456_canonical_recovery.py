import unittest
from fastapi import HTTPException
from pydantic import ValidationError
from app.multimodal_executor_step456.engine import MultimodalExecuteRequest,MultimodalChannel,execute_multimodal
def channel(cid,modality='text',size=4):
    return MultimodalChannel(channel_id=cid,modality=modality,size_bytes=size)
class Step456Tests(unittest.TestCase):
    def test_text_route(self):
        r=execute_multimodal(MultimodalExecuteRequest(session_id='x',channels=[channel('a')]))
        self.assertEqual(r.routes[0].pipeline,'nlp_core')
    def test_all_modalities(self):
        r=execute_multimodal(MultimodalExecuteRequest(session_id='x',channels=[channel(str(i),m) for i,m in enumerate(['text','audio','video','three_d'])]))
        self.assertEqual(len(r.stats['modalities']),4)
    def test_duplicate_rejected(self):
        with self.assertRaises(HTTPException) as x:execute_multimodal(MultimodalExecuteRequest(session_id='x',channels=[channel('a'),channel('a')]))
        self.assertEqual(x.exception.status_code,422)
    def test_empty_id_rejected(self):
        with self.assertRaises(HTTPException):execute_multimodal(MultimodalExecuteRequest(session_id='x',channels=[channel('')]))
    def test_channel_limit(self):
        with self.assertRaises(ValidationError):MultimodalExecuteRequest(session_id='x',channels=[channel(str(i)) for i in range(129)])
    def test_invalid_modality(self):
        with self.assertRaises(ValidationError):channel('a','live_trading')
    def test_utc_timestamp(self):
        r=execute_multimodal(MultimodalExecuteRequest(session_id='x',channels=[]))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
if __name__=='__main__':unittest.main()
