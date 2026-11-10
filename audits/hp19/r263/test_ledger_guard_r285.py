import sqlite3
import tempfile
import unittest
from pathlib import Path
from ledger_guard import LedgerRejected, require_existing_ledger

class LedgerGuardR285Tests(unittest.TestCase):
    def test_existing_valid_ledger_with_uri_metacharacters(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('ledger?replay.sqlite', 'ledger#replay.sqlite', 'ledger normal.sqlite'):
                path = Path(tmp) / name
                with sqlite3.connect(path) as db:
                    db.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
                self.assertIs(require_existing_ledger(path), False)

    def test_missing_ledger_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'missing?ledger.sqlite'
            with self.assertRaises(LedgerRejected):
                require_existing_ledger(path)
            self.assertFalse(path.exists())

    def test_invalid_schema_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'invalid#ledger.sqlite'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE seen (run_id TEXT)')
            with self.assertRaisesRegex(LedgerRejected, 'LEDGER_SCHEMA_INVALID'):
                require_existing_ledger(path)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'real.sqlite'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            alias = Path(tmp) / 'alias.sqlite'
            alias.symlink_to(path)
            with self.assertRaisesRegex(LedgerRejected, 'LEDGER_MISSING_OR_UNSAFE'):
                require_existing_ledger(alias)

if __name__ == '__main__':
    unittest.main()
