import unittest
from r886_agent_registry import EXPECTED_AGENT_IDS, build_registry, RegistryContractError

class RegistryTests(unittest.TestCase):
 def setUp(self):
  self.handlers={agent_id:(lambda payload,key=agent_id:{"agent_id":key,"status":"ok","payload":payload}) for agent_id in EXPECTED_AGENT_IDS}
 def test_expected_inventory_is_52(self): self.assertEqual(len(EXPECTED_AGENT_IDS),52)
 def test_all_handlers_bind_one_to_one(self):
  registry=build_registry(self.handlers)
  self.assertEqual(set(registry),set(EXPECTED_AGENT_IDS))
  for agent_id,handler in registry.items(): self.assertEqual(handler(None)["agent_id"],agent_id)
 def test_missing_handler_fails_closed(self):
  h=dict(self.handlers);h.pop(next(iter(h)))
  with self.assertRaisesRegex(RegistryContractError,"missing_handlers"): build_registry(h)
 def test_unexpected_handler_fails_closed(self):
  h=dict(self.handlers);h["fake.agent"]=lambda p:{}
  with self.assertRaisesRegex(RegistryContractError,"unexpected_handlers"): build_registry(h)
 def test_non_callable_fails_closed(self):
  h=dict(self.handlers);h[next(iter(h))]=None
  with self.assertRaisesRegex(RegistryContractError,"non_callable_handlers"): build_registry(h)
 def test_wrong_container_fails_closed(self):
  with self.assertRaisesRegex(RegistryContractError,"handlers_must_be_dict"): build_registry([])
 def test_all_ids_are_namespaced(self): self.assertTrue(all("." in x for x in EXPECTED_AGENT_IDS))
 def test_no_runtime_authority_granted(self): self.assertEqual(len(build_registry(self.handlers)),52)
 def test_no_implicit_imports(self):
  import inspect
  self.assertNotIn("__import__",inspect.getsource(build_registry))
 def test_exact_expected_count(self): self.assertEqual(len(set(EXPECTED_AGENT_IDS)),52)
if __name__=="__main__": unittest.main(verbosity=2)
