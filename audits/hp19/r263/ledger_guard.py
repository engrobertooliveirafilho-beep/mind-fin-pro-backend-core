"""R287: deny-only preflight for an existing SQLite replay ledger."""
import sqlite3
from pathlib import Path

class LedgerRejected(ValueError):
    pass

def require_existing_ledger(path):
    path = Path(path).absolute()
    # Reject symlinks in any path component, not just the final SQLite file.
    # Path.is_file() follows ancestor symlinks, which otherwise bypasses R285.
    if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file():
        raise LedgerRejected('LEDGER_MISSING_OR_UNSAFE')
    uri = path.as_uri() + '?mode=ro'
    try:
        with sqlite3.connect(uri, uri=True) as conn:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen'").fetchone()
            if row is None:
                raise LedgerRejected('LEDGER_SCHEMA_MISSING')
            columns = {r[1] for r in conn.execute('PRAGMA table_info(seen)')}
            if not {'run_id', 'digest'}.issubset(columns):
                raise LedgerRejected('LEDGER_SCHEMA_INVALID')
    except sqlite3.Error as exc:
        raise LedgerRejected('LEDGER_UNAVAILABLE') from exc
    return False
