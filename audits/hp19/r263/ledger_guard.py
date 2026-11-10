"""R263 deny-only preflight: never recreate a missing replay ledger."""
import sqlite3
from pathlib import Path

class LedgerRejected(ValueError):
    pass

def require_existing_ledger(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise LedgerRejected('LEDGER_MISSING_OR_UNSAFE')
    try:
        with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as conn:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen'").fetchone()
            if row is None:
                raise LedgerRejected('LEDGER_SCHEMA_MISSING')
            columns = {r[1] for r in conn.execute('PRAGMA table_info(seen)')}
            if not {'run_id', 'digest'}.issubset(columns):
                raise LedgerRejected('LEDGER_SCHEMA_INVALID')
    except sqlite3.Error as exc:
        raise LedgerRejected('LEDGER_UNAVAILABLE') from exc
    return False
