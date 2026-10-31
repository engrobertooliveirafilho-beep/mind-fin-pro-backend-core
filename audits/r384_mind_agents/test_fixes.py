import unittest
from safe_dispatch import run_agent, AgentDispatchError
from safe_adapter import run_mind_talk_v2
from safe_registry import build_proposal

class FixTests(unittest.TestCase):
    def test_selected_agent(self):
        self.assertEqual(run_agent("a", registry={"a":lambda p:{"selected":"a"}})["selected"],"a")
    def test_missing_agent(self):
        with self.assertRaises(AgentDispatchError): run_agent("z", registry={})
    def test_adapter_keywords(self):
        r=run_mind_talk_v2("u","hi",execute=lambda **kw:{"tools":[{"ok":True,"payload":{"status":"completed"}}],"args":kw})
        self.assertEqual(r["args"]["prompt"],"hi")
    def test_adapter_stub(self):
        with self.assertRaises(ValueError):
            run_mind_talk_v2("u","hi",execute=lambda **kw:{"tools":[{"ok":True,"payload":{"status":"stub"}}]})
    def test_registry_unverified(self):
        self.assertEqual(build_proposal("a",{"a":{"fields":["x"]}})["status"],"draft_unverified")
if __name__=="__main__":unittest.main()
