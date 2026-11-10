import sqlite3
import tempfile
import unittest
from pathlib import Path
from ledger_guard import LedgerRejected, require_existing_ledger

class LedgerGuardR287Tests(unittest.TestCase):
    def test_ancestor_symlink_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / 'real'
            real.mkdir()
            db = real / 'ledger.sqlite'
            with sqlite3.connect(db) as con:
                con.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            alias = root / 'alias'
            alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(LedgerRejected, 'LEDGER_MISSING_OR_UNSAFE'):
                require_existing_ledger(alias / 'ledger.sqlite')
            self.assertIs(require_existing_ledger(db), False)

    def test_nested_ancestor_symlink_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / 'real'
            (real / 'sub').mkdir(parents=True)
            db = real / 'sub' / 'ledger.sqlite'
            with sqlite3.connect(db) as con:
                con.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            (root / 'alias').symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(LedgerRejected, 'LEDGER_MISSING_OR_UNSAFE'):
                require_existing_ledger(root / 'alias' / 'sub' / 'ledger.sqlite')

    def test_valid_and_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'ledger?#.sqlite'
            with sqlite3.connect(db) as con:
                con.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            self.assertIs(require_existing_ledger(db), False)
            missing = Path(tmp) / 'missing.sqlite'
            with self.assertRaises(LedgerRejected):
                require_existing_ledger(missing)
            self.assertFalse(missing.exists())
