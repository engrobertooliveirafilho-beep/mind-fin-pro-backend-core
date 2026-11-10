"""R261 regression: signed file integrity does not imply identity, freshness, or behavior."""
import sys, unittest
from pathlib import Path
# In offline workspace, place R260's combined_gate.py and test_combined_gate.py on PYTHONPATH.
from test_combined_gate import CombinedTests
from combined_gate import inspect

class ScopeReplayTests(CombinedTests):
    def test_arbitrary_noncanonical_agents_pass_integrity(self):
        result=inspect(self.root,self.envelope,self.trusted)
        self.assertTrue(result['files_verified'])
        self.assertEqual({e['agent_id'] for e in self.manifest['entries']},
                         {f'agent_test_{i:02d}' for i in range(19)})
        self.assertFalse(result['certified'])
    def test_identical_signed_manifest_replay_accepted(self):
        first=inspect(self.root,self.envelope,self.trusted)
        second=inspect(self.root,self.envelope,self.trusted)
        self.assertEqual(first,second)
        self.assertFalse(second['certified'])
    def test_fake_source_with_matching_digest_accepted(self):
        self.assertEqual((self.root/'agent_test_00.py').read_bytes(),b'def run(): return None\n')
        result=inspect(self.root,self.envelope,self.trusted)
        self.assertTrue(result['files_verified'])
        self.assertFalse(result['certified'])
