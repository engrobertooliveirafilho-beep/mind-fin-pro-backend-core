import unittest
from r885_agent_registry_audit import audit_registry

def good():
 return {"agents":[{"id":"a","step_ids":[1,2],"governance_rules":{"can_block_actions":False,"can_change_code":False},"agent_health":{"status":"healthy"},"active":True}]}
class Tests(unittest.TestCase):
 def test_valid_registry(self): self.assertEqual(audit_registry(good())["status"],"metadata_consistent")
 def test_invalid_json(self): self.assertEqual(audit_registry("{")["reason"],"invalid_json")
 def test_bad_shape(self): self.assertEqual(audit_registry({"agents":{}})["reason"],"invalid_registry_shape")
 def test_duplicate_ids(self):
  d=good();d["agents"].append(dict(d["agents"][0]));self.assertIn("duplicate_agent_id",[x["kind"] for x in audit_registry(d)["findings"]])
 def test_block_authority(self):
  d=good();d["agents"][0]["governance_rules"]["can_block_actions"]=True;self.assertIn("unsafe_agent_block_authority",[x["kind"] for x in audit_registry(d)["findings"]])
 def test_autorun_not_authority(self):
  d=good();d["agents"][0]["auto_run"]=True;self.assertIn("autorun_flag_not_authority",[x["kind"] for x in audit_registry(d)["findings"]])
 def test_active_unknown_health(self):
  d=good();d["agents"][0]["agent_health"]["status"]="unknown";k=[x["kind"] for x in audit_registry(d)["findings"]];self.assertIn("active_without_health_proof",k)
 def test_no_dispatch_ever(self): self.assertFalse(audit_registry(good())["dispatch_authorized"])
 def test_no_runtime_cert(self): self.assertFalse(audit_registry(good())["runtime_certified"])
 def test_bool_step_rejected(self):
  d=good();d["agents"][0]["step_ids"]=[True];self.assertIn("invalid_step_ids",[x["kind"] for x in audit_registry(d)["findings"]])
if __name__=="__main__":unittest.main(verbosity=2)
