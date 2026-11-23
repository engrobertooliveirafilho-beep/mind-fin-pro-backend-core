import unittest
from r830_dispatch_contract import run_agent, AgentDispatchError

class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.registry={"alpha": lambda payload: {"status":"ok","echo":payload}}
    def test_exact_handler_selected(self):
        self.assertEqual(run_agent("alpha", {"x":1}, registry=self.registry)["echo"], {"x":1})
    def test_unknown_agent_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"agent_not_registered"): run_agent("missing", registry=self.registry)
    def test_missing_registry_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"agent_not_registered"): run_agent("alpha")
    def test_invalid_id_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"invalid_agent_id"): run_agent(" ", registry=self.registry)
    def test_non_callable_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"agent_handler_not_callable"): run_agent("alpha", registry={"alpha":None})
    def test_non_dict_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"invalid_agent_result"): run_agent("alpha", registry={"alpha":lambda p:"ok"})
    def test_stub_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"nonfunctional_agent_result"): run_agent("alpha", registry={"alpha":lambda p:{"status":"not_implemented","mode":"stub"}})
    def test_error_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"nonfunctional_agent_result"): run_agent("alpha", registry={"alpha":lambda p:{"status":"error"}})
    def test_identity_mismatch_rejected(self):
        with self.assertRaisesRegex(AgentDispatchError,"agent_identity_mismatch"): run_agent("alpha", registry={"alpha":lambda p:{"agent_id":"beta","status":"ok"}})
    def test_no_dynamic_imports(self):
        import inspect
        source=inspect.getsource(run_agent)
        self.assertNotIn("__import__", source)
        self.assertNotIn("importlib", source)
if __name__=="__main__": unittest.main(verbosity=2)
