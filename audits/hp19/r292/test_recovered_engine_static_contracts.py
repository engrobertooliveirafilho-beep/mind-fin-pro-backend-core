import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).parent

class RecoveredEngineStaticContracts(unittest.TestCase):
    def source(self, name):
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        return text, ast.parse(text)

    def test_distributed_assignment_is_single_best_cluster_per_agent(self):
        source, tree = self.source('recovered_step450_distributed_agents.py')
        self.assertIn('best_cluster_id', source)
        comps = [n for n in ast.walk(tree) if isinstance(n, ast.DictComp)]
        self.assertTrue(comps)
        self.assertTrue(any(isinstance(n.value, ast.Attribute) and isinstance(n.value.value, ast.Call) for n in comps))

    def test_distributed_fanout_is_logical_replication(self):
        source, _ = self.source('recovered_step450_distributed_agents.py')
        self.assertIn('range(1,request.fanout+1)', source)
        self.assertIn('best_cluster_for_agent', source)

    def test_research_routes_all_modes_to_stub(self):
        source, tree = self.source('recovered_step452_research_agent.py')
        self.assertIn('research_agent_step452_stub', source)
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == '_make_stub_results' for n in ast.walk(tree)))

    def test_research_sources_are_synthetic(self):
        source, _ = self.source('recovered_step452_research_agent.py')
        self.assertIn('stub://research/', source)
        self.assertIn('simulando pesquisa', source)

if __name__ == '__main__':
    unittest.main()
