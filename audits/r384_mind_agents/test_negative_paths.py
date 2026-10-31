import unittest
from safe_dispatch import run_agent, AgentDispatchError
from safe_adapter import run_mind_talk_v2

class NegativePaths(unittest.TestCase):
    def test_dispatch_missing_callable(self):
        with self.assertRaises(AgentDispatchError):
            run_agent("a",registry={"a":None})
    def test_dispatch_error(self):
        with self.assertRaises(AgentDispatchError):
            run_agent("a",registry={"a":lambda p:{"error":"bad"}})
    def test_adapter_empty_tools(self):
        with self.assertRaises(ValueError):
            run_mind_talk_v2("u","hi",execute=lambda **k:{"tools":[]})
    def test_adapter_failed_tool(self):
        with self.assertRaises(ValueError):
            run_mind_talk_v2("u","hi",execute=lambda **k:{"tools":[{"ok":False,"payload":{}}]})
if __name__=="__main__":unittest.main()
