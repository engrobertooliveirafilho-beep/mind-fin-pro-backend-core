from app.agent_longterm_memory import AgentLongTermMemory


def test_agent_longterm_orders_and_filters_by_agent():
    mem = AgentLongTermMemory()
    mem.add_event('agent1', 's1', 1, 'A')
    mem.add_event('agent1', 's1', 3, 'C')
    mem.add_event('agent1', 's2', 2, 'B')
    mem.add_event('agent2', 's9', 5, 'Z')

    last = mem.last_events('agent1', 2)
    assert len(last) == 2
    assert last[0].endswith('B')
    assert last[1].endswith('C')

