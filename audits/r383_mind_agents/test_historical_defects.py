"""Isolated, dependency-free regressions for the original MIND agent sources.
These tests deliberately prove historical defects; no motor is promoted.
"""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
class HistoricalAgentDefects(unittest.TestCase):
    def test_unified_dispatch_ignores_agent_id(self):
        s=(ROOT/"agents_unified_runtime.py").read_text(encoding="utf-8")
        tree=ast.parse(s)
        fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="run_agent")
        self.assertTrue(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=="get" and any(isinstance(a,ast.Constant) and a.value=="run_dry" for a in x.args) for x in ast.walk(fn)))
        self.assertFalse(any(isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id in ("AGENTS","REGISTRY","DISPATCH") for x in ast.walk(fn)))
    def test_mind_adapter_positional_call(self):
        s=(ROOT/"mind_talk_runtime_adapter.py").read_text(encoding="utf-8")
        tree=ast.parse(s)
        calls=[x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="run_agent_turn_as_dict"]
        self.assertEqual(len(calls),1)
        self.assertEqual(len(calls[0].args),1)
        self.assertEqual(len(calls[0].keywords),0)
    def test_agent_runtime_keyword_only_signature(self):
        s=(ROOT/"agent_runtime.py").read_text(encoding="utf-8")
        tree=ast.parse(s)
        fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="run_agent_turn_as_dict")
        self.assertEqual(len(fn.args.args),0)
        self.assertIn("prompt",[a.arg for a in fn.args.kwonlyargs])
    def test_stub_false_success(self):
        s=(ROOT/"agent_runtime.py").read_text(encoding="utf-8")
        tree=ast.parse(s)
        fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="_exec_chat_llm")
        self.assertTrue(any(isinstance(x,ast.Constant) and x.value=="stub" for x in ast.walk(fn)))
        self.assertTrue(any(isinstance(x,ast.keyword) and x.arg=="ok" and isinstance(x.value,ast.Constant) and x.value.value is True for x in ast.walk(fn)))
    def test_registry_import_scheduler_side_effect(self):
        s=(ROOT/"agents_runtime.py").read_text(encoding="utf-8")
        tree=ast.parse(s)
        self.assertTrue(any(isinstance(x,ast.Try) and any(isinstance(y,ast.Call) and isinstance(y.func,ast.Name) and y.func.id=="start_scheduler" for y in ast.walk(x)) for x in tree.body))
if __name__=="__main__": unittest.main()
