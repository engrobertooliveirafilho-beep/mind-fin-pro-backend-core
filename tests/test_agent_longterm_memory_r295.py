import tempfile
import unittest
from pathlib import Path
from app.agent_longterm_memory import AgentLongTermMemory

class R295MemoryTests(unittest.TestCase):
    def test_limit_zero_returns_empty(self):
        m=AgentLongTermMemory(); m.add_event('a','s',1,'one')
        self.assertEqual(m.last_events('a',0), [])
    def test_negative_limit_rejected(self):
        m=AgentLongTermMemory()
        with self.assertRaises(ValueError): m.last_events('a',-1)
    def test_orders_by_timestamp_stably(self):
        m=AgentLongTermMemory()
        m.add_event('a','s',3,'C'); m.add_event('a','s',1,'A'); m.add_event('a','s',1,'B')
        self.assertEqual(m.last_events('a',3), ['[s] A','[s] B','[s] C'])
    def test_filters_agent_and_caps_results(self):
        m=AgentLongTermMemory()
        for i in range(5): m.add_event('a','s',i,str(i))
        m.add_event('b','s',9,'other')
        self.assertEqual(m.last_events('a',2), ['[s] 3','[s] 4'])
    def test_sqlite_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'memory.sqlite'
            first=AgentLongTermMemory(str(db)); first.add_event('agent','sess',1,'durable')
            second=AgentLongTermMemory(str(db))
            self.assertEqual(second.last_events('agent'), ['[sess] durable'])
    def test_sqlite_isolates_agents(self):
        with tempfile.TemporaryDirectory() as d:
            m=AgentLongTermMemory(str(Path(d)/'memory.sqlite'))
            m.add_event('a','s',1,'A'); m.add_event('b','s',2,'B')
            self.assertEqual(m.last_events('a'), ['[s] A'])
    def test_sqlite_zero_limit_and_order(self):
        with tempfile.TemporaryDirectory() as d:
            m=AgentLongTermMemory(str(Path(d)/'memory.sqlite'))
            m.add_event('a','s',3,'C'); m.add_event('a','s',1,'A'); m.add_event('a','s',1,'B')
            self.assertEqual(m.last_events('a',0), [])
            self.assertEqual(m.last_events('a',3), ['[s] A','[s] B','[s] C'])
    def test_invalid_event_rejected(self):
        m=AgentLongTermMemory()
        with self.assertRaises(ValueError): m.add_event('', 's', 1, 'x')
        with self.assertRaises(ValueError): m.add_event('a', 's', True, 'x')
    def test_invalid_limit_rejected(self):
        m=AgentLongTermMemory()
        with self.assertRaises(ValueError): m.last_events('a', True)

if __name__=='__main__': unittest.main()
