import unittest
from pydantic import ValidationError
from app.cognition.hierarchical_planner_step449.engine import HierarchicalPlanRequest,plan_hierarchy
class Step449Tests(unittest.TestCase):
    def test_three_levels(self):
        r=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit'))
        self.assertEqual(len(r.nodes),10)
    def test_one_level(self):
        r=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit',depth=1))
        self.assertEqual(len(r.nodes),1)
    def test_two_levels(self):
        r=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit',depth=2))
        self.assertEqual(len(r.nodes),4)
    def test_stable_key(self):
        a=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit'))
        b=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit'))
        self.assertEqual(a.memory_snapshot['memory_key'],b.memory_snapshot['memory_key'])
    def test_override_key(self):
        r=plan_hierarchy(HierarchicalPlanRequest(goal='paper audit',memory_key='explicit'))
        self.assertEqual(r.memory_snapshot['memory_key'],'explicit')
    def test_empty_goal(self):
        with self.assertRaises(ValidationError):HierarchicalPlanRequest(goal='')
    def test_context_limit(self):
        with self.assertRaises(ValidationError):HierarchicalPlanRequest(goal='a',context='x'*8193)
    def test_utc(self):
        self.assertTrue(plan_hierarchy(HierarchicalPlanRequest(goal='paper audit')).meta['created_at'].endswith('Z'))
