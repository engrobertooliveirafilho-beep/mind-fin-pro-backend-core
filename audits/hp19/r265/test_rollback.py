import sys,sqlite3,unittest
sys.path[:0]=['/mnt/data/HP19_R264','/mnt/data/HP19_R262','/mnt/data/HP19_R260']
from test_replay_gate import R264Tests
from replay_gate import inspect_once

class RollbackRegression(R264Tests):
    def test_replaced_ledger_reaccepts_old_run(self):
        with sqlite3.connect(self.ledger) as db:
            db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        snapshot=self.ledger.read_bytes()
        first=inspect_once(self.root,self.envelope,self.trusted,self.ledger)
        self.assertTrue(first['replay_recorded'])
        self.ledger.write_bytes(snapshot)
        second=inspect_once(self.root,self.envelope,self.trusted,self.ledger)
        self.assertTrue(second['replay_recorded'])
        self.assertFalse(second['certified'])
if __name__=='__main__':unittest.main()
