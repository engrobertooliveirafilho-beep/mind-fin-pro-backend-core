import unittest
from r832 import inspect_source,inspect_paths
class Tests(unittest.TestCase):
    def test_alias(self): self.assertFalse(inspect_source('import importlib as i\ni.import_module("x")')['safe'])
    def test_from_alias(self): self.assertFalse(inspect_source('from importlib import import_module as x\nx("a")')['safe'])
    def test_report(self): self.assertFalse(inspect_source('capability_recovery_report()')['safe'])
    def test_memory_write(self): self.assertFalse(inspect_source('mod.store_social_memory()')['safe'])
    def test_constructor(self): self.assertFalse(inspect_source('cls()')['safe'])
    def test_safe(self): self.assertTrue(inspect_source('x=3')['safe'])
    def test_syntax(self): self.assertFalse(inspect_source('def (')['safe'])
    def test_missing(self): self.assertFalse(inspect_paths(['/no/r832.py'])['/no/r832.py']['safe'])
if __name__=='__main__': unittest.main()
