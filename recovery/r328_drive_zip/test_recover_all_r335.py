import json,tempfile,unittest
from pathlib import Path
from recover_all import recover
class RecoveryGateTests(unittest.TestCase):
 def test_empty_queue_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/"q.jsonl";q.write_text("")
   with self.assertRaises(ValueError):recover(q,Path(d)/"out")
 def test_duplicate_id_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/"q.jsonl";r={"id":"A"*20,"size":1};q.write_text(json.dumps(r)+"\n"+json.dumps(r)+"\n")
   with self.assertRaises(ValueError):recover(q,Path(d)/"out")
 def test_invalid_size_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/"q.jsonl";q.write_text(json.dumps({"id":"A"*20,"size":-1})+"\n")
   with self.assertRaises(ValueError):recover(q,Path(d)/"out")
if __name__=="__main__":unittest.main()
