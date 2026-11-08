"""Isolated, read-only R6 approval gate; durable incremental ledger (not code promotion)."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import time

HEX = set('0123456789abcdef')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def check_hash(value):
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX

def approvals(path):
    result = {}
    if path is None:
        return result
    with open(path, 'rb') as f:
        for raw in f:
            if not raw.endswith(b'\n'):
                raise ValueError('PARTIAL_APPROVAL_MANIFEST')
            item = json.loads(raw)
            if set(item) != {'r6_sha256', 'r4_sha256', 'r5_sha256', 'decision', 'authority'}:
                raise ValueError('INVALID_APPROVAL_SCHEMA')
            if any(not check_hash(item[k]) for k in ('r6_sha256','r4_sha256','r5_sha256')):
                raise ValueError('INVALID_APPROVAL_HASH')
            if item['decision'] != 'APPROVED' or not isinstance(item['authority'], str) or not item['authority'].strip():
                raise ValueError('INVALID_APPROVAL_AUTHORITY')
            key = item['r6_sha256']
            if key in result and result[key] != item:
                raise ValueError('CONFLICTING_APPROVAL')
            result[key] = item
    return result

def consume(source, db_path, approval_path=None, limit=1000):
    """Consume complete R6 lines once; keep unapproved entries pending for later promotion."""
    source = Path(source).resolve(strict=True)
    db_path = Path(db_path).resolve()
    if limit < 1 or source == db_path or (approval_path is not None and source == Path(approval_path).resolve()):
        raise ValueError('INVALID_PATH_OR_LIMIT')
    if approval_path and Path(approval_path).resolve() == db_path:
        raise ValueError('APPROVAL_DB_COLLISION')
    approved = approvals(approval_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path, timeout=5)
    try:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA synchronous=FULL')
        db.executescript("""CREATE TABLE IF NOT EXISTS cursor(id INTEGER PRIMARY KEY CHECK(id=1), source TEXT NOT NULL, offset INTEGER NOT NULL, prefix_sha256 TEXT NOT NULL, seq INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS records(r6_sha256 TEXT PRIMARY KEY, seq INTEGER UNIQUE NOT NULL, r4_sha256 TEXT NOT NULL, r5_sha256 TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('PENDING','APPROVED')), authority TEXT);
        """)
        cursor = db.execute('SELECT source,offset,prefix_sha256,seq FROM cursor WHERE id=1').fetchone()
        offset = cursor[1] if cursor else 0
        seq = cursor[3] if cursor else 0
        if cursor and cursor[0] != str(source):
            raise ValueError('SOURCE_BINDING_CHANGED')
        if source.stat().st_size < offset:
            raise ValueError('SOURCE_TRUNCATED')
        with source.open('rb') as f:
            prefix = f.read(offset)
            if cursor and sha(prefix) != cursor[2]:
                raise ValueError('SOURCE_PREFIX_CHANGED')
            f.seek(offset)
            processed = 0
            promoted = 0
            with db:
                for digest, r4, r5 in db.execute("SELECT r6_sha256,r4_sha256,r5_sha256 FROM records WHERE decision='PENDING'"):
                    a = approved.get(digest)
                    if a:
                        if a['r4_sha256'] != r4 or a['r5_sha256'] != r5:
                            raise ValueError('APPROVAL_LINEAGE_MISMATCH')
                        db.execute("UPDATE records SET decision='APPROVED',authority=? WHERE r6_sha256=?", (a['authority'], digest))
                        promoted += 1
                while processed < limit:
                    raw = f.readline()
                    if not raw or not raw.endswith(b'\n'):
                        break
                    item = json.loads(raw)
                    if set(item) != {'stage','seq','r5_seq','r4_sha256','r5_sha256'} or item['stage'] != 'R6' or type(item['seq']) is not int or item['seq'] != seq+1 or type(item['r5_seq']) is not int or item['r5_seq'] != item['seq'] or not check_hash(item['r4_sha256']) or not check_hash(item['r5_sha256']):
                        raise ValueError('R6_CONTRACT_MISMATCH')
                    digest = sha(raw)
                    a = approved.get(digest)
                    if a and (a['r4_sha256'] != item['r4_sha256'] or a['r5_sha256'] != item['r5_sha256']):
                        raise ValueError('APPROVAL_LINEAGE_MISMATCH')
                    decision = 'APPROVED' if a else 'PENDING'
                    db.execute('INSERT INTO records VALUES(?,?,?,?,?,?)', (digest,item['seq'],item['r4_sha256'],item['r5_sha256'],decision,a['authority'] if a else None))
                    seq += 1
                    processed += 1
                    offset = f.tell()
                f.seek(0)
                prefix_hash = sha(f.read(offset))
                db.execute('INSERT INTO cursor VALUES(1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET offset=excluded.offset,prefix_sha256=excluded.prefix_sha256,seq=excluded.seq', (str(source),offset,prefix_hash,seq))
        totals = dict(db.execute('SELECT decision,COUNT(*) FROM records GROUP BY decision'))
        return {'processed':processed,'promoted':promoted,'total':seq,'approved':totals.get('APPROVED',0),'pending':totals.get('PENDING',0),'offset':offset,'source_bytes':source.stat().st_size,'time_unix':time.time()}
    finally:
        db.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--r6',required=True)
    p.add_argument('--db',required=True)
    p.add_argument('--approvals')
    p.add_argument('--batch',type=int,default=1000)
    p.add_argument('--interval',type=float,default=10)
    p.add_argument('--once',action='store_true')
    a=p.parse_args()
    if a.interval < 1:
        p.error('interval must be >=1')
    while True:
        print(json.dumps(consume(a.r6,a.db,a.approvals,a.batch),sort_keys=True),flush=True)
        if a.once:
            break
        time.sleep(a.interval)

if __name__ == '__main__':
    main()
