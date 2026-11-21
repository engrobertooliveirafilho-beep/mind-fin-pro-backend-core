from __future__ import annotations
from typing import Dict, Any


def compute_gpu_scaling_decision(
    queue_length: int,
    avg_latency_ms: float,
    current_instances: int,
    min_instances: int = 0,
    max_instances: int = 64,
    target_latency_ms: float = 1500.0,
    cost_sensitivity: float = 1.0,
) -> Dict[str, Any]:
    q = max(0, int(queue_length))
    cur = max(0, int(current_instances))
    min_i = max(0, int(min_instances))
    max_i = max(min_i + 1, int(max_instances))

    if cur < min_i:
        cur = min_i
    if cur > max_i:
        cur = max_i

    latency = max(1.0, float(avg_latency_ms))
    target = max(1.0, float(target_latency_ms))
    sensitivity = max(0.1, float(cost_sensitivity))

    pressure_q = q / 10.0
    pressure_latency = latency / target

    pressure = pressure_q * 0.6 + pressure_latency * 0.4

    desired = cur

    if pressure > 2.0:
        scale_up = int(1 + pressure / sensitivity)
        desired = min(max_i, cur + max(1, scale_up))
        reason = "scale_out_high_pressure"
    elif pressure < 0.7 and q == 0 and latency < target * 0.8:
        scale_down = 1 if sensitivity <= 1.0 else 0
        desired = max(min_i, cur - scale_down)
        reason = "scale_in_low_pressure"
    else:
        reason = "keep_current"

    return {
        "queue_length": q,
        "avg_latency_ms": latency,
        "current_instances": cur,
        "desired_instances": desired,
        "min_instances": min_i,
        "max_instances": max_i,
        "target_latency_ms": target,
        "cost_sensitivity": sensitivity,
        "reason": reason,
        "pressure": pressure,
    }

