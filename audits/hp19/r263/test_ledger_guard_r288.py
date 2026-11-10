import sqlite3
import tempfile
import unittest
from pathlib import Path
from ledger_guard import LedgerRejected, require_existing_ledger

class R288LedgerRegression(unittest.TestCase):
    def test_valid_uri_metacharacters(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'ledger?#.sqlite'
            with sqlite3.connect(p) as c:
                c.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            self.assertIs(require_existing_ledger(p), False)

    def test_missing_never_created(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'absent.sqlite'
            with self.assertRaises(LedgerRejected):
                require_existing_ledger(p)
            self.assertFalse(p.exists())

    def test_ancestor_symlink_denied(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / 'real').mkdir()
            p = base / 'real' / 'db.sqlite'
            with sqlite3.connect(p) as c:
                c.execute('CREATE TABLE seen (run_id TEXT, digest TEXT)')
            (base / 'alias').symlink_to(base / 'real', target_is_directory=True)
            with self.assertRaisesRegex(LedgerRejected, 'UNSAFE'):
                require_existing_ledger(base / 'alias' / 'db.sqlite')

    def test_invalid_schema(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.sqlite'
            with sqlite3.connect(p) as c:
                c.execute('CREATE TABLE seen (run_id TEXT)')
            with self.assertRaisesRegex(LedgerRejected, 'SCHEMA_INVALID'):
                require_existing_ledger(p)

    def test_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.sqlite'
            p.write_text('not sqlite')
            with self.assertRaisesRegex(LedgerRejected, 'UNAVAILABLE'):
                require_existing_ledger(p)

if __name__ == '__main__':
    unittest.main()
