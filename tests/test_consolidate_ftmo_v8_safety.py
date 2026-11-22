"""V8 PAPER consolidation evidence-immutability regressions."""
import tempfile
import unittest
from pathlib import Path
from tools.consolidate_ftmo_v8 import run

class ConsolidationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'source'
        self.source.mkdir()

    def test_reject_same_source_output(self):
        with self.assertRaises(ValueError):
            run(self.source,self.source)

    def test_reject_output_below_source(self):
        with self.assertRaises(ValueError):
            run(self.source,self.source/'reports')

    def test_reject_output_ancestor_of_source(self):
        with self.assertRaises(ValueError):
            run(self.source,self.root)

    def test_reject_existing_evidence(self):
        out=self.root/'evidence'
        out.mkdir()
        (out/'REGRESSION_V8.txt').write_text('immutable')
        with self.assertRaises(ValueError):
            run(self.source,out)
        self.assertEqual((out/'REGRESSION_V8.txt').read_text(),'immutable')

    def test_missing_sources_fail_closed(self):
        out=self.root/'empty-output'
        self.assertEqual(run(self.source,out),2)
        self.assertIn('"ftmo_release": "BLOCKED"',(out/'CONSOLIDATION_V8.json').read_text())
