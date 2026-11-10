"""Fail-closed pure scheduler extracted from Step450 findings; not wired into runtime."""
from typing import Iterable

class DispatchRejected(ValueError):
    pass

def allocate_shards(clusters: Iterable[dict], agents: Iterable[dict], fanout: int = 2):
    clusters = list(clusters)
    agents = list(agents)
    if not isinstance(fanout, int) or isinstance(fanout, bool) or not 1 <= fanout <= 10:
        raise DispatchRejected("INVALID_FANOUT")
    if not clusters or not agents:
        raise DispatchRejected("EMPTY_TOPOLOGY")
    cluster_ids = [c.get("cluster_id") for c in clusters]
    agent_ids = [a.get("agent_id") for a in agents]
    if any(not isinstance(x, str) or not x.strip() for x in cluster_ids + agent_ids):
        raise DispatchRejected("INVALID_ID")
    if len(set(cluster_ids)) != len(cluster_ids):
        raise DispatchRejected("DUPLICATE_CLUSTER_ID")
    if len(set(agent_ids)) != len(agent_ids):
        raise DispatchRejected("DUPLICATE_AGENT_ID")
    for c in clusters:
        if not isinstance(c.get("capacity"), int) or isinstance(c.get("capacity"), bool) or c["capacity"] < 1:
            raise DispatchRejected("INVALID_CAPACITY")
        if not isinstance(c.get("latency_ms"), (int, float)) or c["latency_ms"] < 0:
            raise DispatchRejected("INVALID_LATENCY")
    for a in agents:
        if not isinstance(a.get("weight", 0.5), (int, float)) or not 0 <= a.get("weight", 0.5) <= 1:
            raise DispatchRejected("INVALID_WEIGHT")
    requested = len(agents) * fanout
    available = sum(c["capacity"] for c in clusters)
    if requested > available:
        raise DispatchRejected("INSUFFICIENT_CAPACITY")
    remaining = {c["cluster_id"]: c["capacity"] for c in clusters}
    by_id = {c["cluster_id"]: c for c in clusters}
    assignments = []
    for agent in sorted(agents, key=lambda x: x["agent_id"]):
        for shard in range(1, fanout + 1):
            eligible = [c for c in clusters if remaining[c["cluster_id"]] > 0]
            # Prefer available capacity while penalizing latency; stable ID tie-break.
            chosen = min(eligible, key=lambda c: (
                -(remaining[c["cluster_id"]] / c["capacity"]) * (0.5 + agent.get("weight", 0.5)) / (1 + c["latency_ms"] / 100),
                c["cluster_id"],
            ))
            cid = chosen["cluster_id"]
            remaining[cid] -= 1
            assignments.append({"cluster_id": cid, "agent_id": agent["agent_id"],
                "role": agent["role"], "shard_index": shard,
                "remaining_capacity": remaining[cid], "reason": "capacity_latency_aware"})
    return assignments
