"""Fail-closed pure scheduler; isolated adapter, not wired into runtime."""
import math
from typing import Iterable

class DispatchRejected(ValueError):
    pass

_ALLOWED_ROLES = {"orchestrator", "toolmaster", "researcher", "analyzer", "planner"}

def allocate_shards(clusters: Iterable[dict], agents: Iterable[dict], fanout: int = 2):
    clusters, agents = list(clusters), list(agents)
    if not isinstance(fanout, int) or isinstance(fanout, bool) or not 1 <= fanout <= 10:
        raise DispatchRejected("INVALID_FANOUT")
    if not clusters or not agents:
        raise DispatchRejected("EMPTY_TOPOLOGY")
    try:
        cluster_ids = [c["cluster_id"] for c in clusters]
        agent_ids = [a["agent_id"] for a in agents]
    except (KeyError, TypeError):
        raise DispatchRejected("INVALID_RECORD")
    if any(not isinstance(x, str) or not x.strip() for x in cluster_ids + agent_ids):
        raise DispatchRejected("INVALID_ID")
    if len(set(cluster_ids)) != len(cluster_ids):
        raise DispatchRejected("DUPLICATE_CLUSTER_ID")
    if len(set(agent_ids)) != len(agent_ids):
        raise DispatchRejected("DUPLICATE_AGENT_ID")
    for c in clusters:
        cap, latency = c.get("capacity"), c.get("latency_ms")
        if not isinstance(cap, int) or isinstance(cap, bool) or cap < 1:
            raise DispatchRejected("INVALID_CAPACITY")
        if isinstance(latency, bool) or not isinstance(latency, (int, float)) or not math.isfinite(latency) or latency < 0:
            raise DispatchRejected("INVALID_LATENCY")
    for a in agents:
        weight, role = a.get("weight", 0.5), a.get("role")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or not 0 <= weight <= 1:
            raise DispatchRejected("INVALID_WEIGHT")
        if role not in _ALLOWED_ROLES:
            raise DispatchRejected("INVALID_ROLE")
    if len(agents) * fanout > sum(c["capacity"] for c in clusters):
        raise DispatchRejected("INSUFFICIENT_CAPACITY")
    remaining = {c["cluster_id"]: c["capacity"] for c in clusters}
    assignments = []
    for agent in sorted(agents, key=lambda x: x["agent_id"]):
        for shard in range(1, fanout + 1):
            eligible = [c for c in clusters if remaining[c["cluster_id"]] > 0]
            chosen = min(eligible, key=lambda c: (
                -(remaining[c["cluster_id"]] / c["capacity"]) / (1 + c["latency_ms"] / 100),
                c["cluster_id"],
            ))
            cid = chosen["cluster_id"]
            remaining[cid] -= 1
            assignments.append({"cluster_id": cid, "agent_id": agent["agent_id"],
                "role": agent["role"], "shard_index": shard,
                "remaining_capacity": remaining[cid], "reason": "capacity_latency_aware"})
    return assignments
