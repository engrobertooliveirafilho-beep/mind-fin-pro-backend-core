def allocate(clusters, agents, fanout):
    if not 1 <= fanout <= 10:
        raise ValueError('invalid fanout')
    remaining = {c.cluster_id: c.capacity for c in clusters}
    if len(remaining) != len(clusters) or len({a.agent_id for a in agents}) != len(agents):
        raise ValueError('duplicate identifier')
    assignments = []
    ordered = sorted(agents, key=lambda a: (-a.weight, a.agent_id))
    for shard in range(1, fanout + 1):
        for agent in ordered:
            available = [c for c in clusters if remaining[c.cluster_id] > 0]
            if not available:
                return assignments
            c = min(available, key=lambda c: (-remaining[c.cluster_id]/(1+c.latency_ms/100), c.cluster_id))
            remaining[c.cluster_id] -= 1
            assignments.append((c.cluster_id, agent.agent_id, shard))
    return assignments
