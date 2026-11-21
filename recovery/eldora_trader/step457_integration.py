"""Fail-closed adapter for recovered STEP457 decision engine (no GPU actions)."""
import math

class PolicyViolation(ValueError):
    pass

def guarded_decision(decision_engine, *, queue_length, avg_latency_ms, current_instances,
                     min_instances=0, max_instances=64, target_latency_ms=1500.0,
                     cost_sensitivity=1.0, cost_limit_brl=0):
    """Compute a recommendation but never authorize paid scaling or GPU operations."""
    ints = (queue_length, current_instances, min_instances, max_instances)
    if any(type(v) is not int for v in ints) or not (queue_length >= 0 and 0 <= min_instances <= current_instances <= max_instances and max_instances > 0):
        raise PolicyViolation('invalid capacity constraints')
    floats = (avg_latency_ms, target_latency_ms, cost_sensitivity)
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in floats):
        raise PolicyViolation('invalid finite positive metrics')
    if type(cost_limit_brl) not in (int, float) or not math.isfinite(cost_limit_brl) or cost_limit_brl != 0:
        raise PolicyViolation('cost limit must be exactly zero')
    if not callable(decision_engine):
        raise PolicyViolation('decision engine unavailable')
    result = decision_engine(queue_length=queue_length, avg_latency_ms=avg_latency_ms,
                             current_instances=current_instances, min_instances=min_instances,
                             max_instances=max_instances, target_latency_ms=target_latency_ms,
                             cost_sensitivity=cost_sensitivity)
    if not isinstance(result, dict) or type(result.get('desired_instances')) is not int:
        raise PolicyViolation('invalid decision engine result')
    desired = result['desired_instances']
    if desired < min_instances or desired > max_instances:
        raise PolicyViolation('decision outside capacity limits')
    return {'current_instances': current_instances, 'proposed_instances': desired,
            'authorized_instances': current_instances, 'authorized_to_execute': False,
            'action': 'NO_OP', 'cost_limit_brl': 0,
            'blocked_scale_out': desired > current_instances,
            'reason': 'PAPER_ONLY_ZERO_COST'}
