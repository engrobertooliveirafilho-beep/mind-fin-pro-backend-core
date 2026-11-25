import sqlite3
from contextlib import closing

class PersistentMetricsRegistry:
    def __init__(self, path):
        self.path = str(path)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS turns(profile TEXT PRIMARY KEY, n INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS tools(profile TEXT, outcome TEXT, kind TEXT, n INTEGER NOT NULL, PRIMARY KEY(profile,outcome,kind))')

    def record_turn(self, profile_key, tools_success, tools_fail):
        profile = profile_key or 'unknown'
        if isinstance(tools_success, str) or isinstance(tools_fail, str):
            raise ValueError('Expected collections of tool keys')
        success, fail = tuple(tools_success), tuple(tools_fail)
        if not isinstance(profile, str) or any(not isinstance(k,str) or not k for k in success+fail):
            raise ValueError('Invalid metric key')
        with closing(sqlite3.connect(self.path, timeout=0.1)) as db, db:
            db.execute('INSERT INTO turns VALUES (?,1) ON CONFLICT(profile) DO UPDATE SET n=n+1',(profile,))
            for outcome, keys in [('success',success),('fail',fail)]:
                db.executemany('INSERT INTO tools VALUES (?,?,?,1) ON CONFLICT(profile,outcome,kind) DO UPDATE SET n=n+1',[(profile,outcome,k) for k in keys])

    def snapshot(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('BEGIN')
            result={p:{'turns_total':n,'tools_success_by_kind':{},'tools_fail_by_kind':{}} for p,n in db.execute('SELECT profile,n FROM turns')}
            for p,o,k,n in db.execute('SELECT profile,outcome,kind,n FROM tools'):
                result[p]['tools_'+o+'_by_kind'][k]=n
            return result
