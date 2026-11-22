"""P2298 decision reconciliation. Historical approval is not runtime authorization."""
import math

REQUIRED_RESTRICTIONS = frozenset({
    'GER40_CONCENTRATION_RISK', 'PAPER_FORWARD_REQUIRED',
    'MONTE_CARLO_REQUIRED', 'SPREAD_SLIPPAGE_STRESS_REQUIRED',
    'MT5_DEMO_CONSUMPTION_REQUIRED', 'PERFORMANCE_MONITOR_REQUIRED',
})

def reconcile_decision(decision, candidates):
    if not isinstance(decision, dict) or not isinstance(candidates, (list, tuple)):
        raise ValueError('P2298_INVALID_INPUT')
    if decision.get('decision') != 'APPROVE_FOR_PAPER_WATCH_ONLY' or decision.get('mode') != 'PAPER_ONLY' or decision.get('real_orders') != 'FORBIDDEN' or decision.get('ftmo_real') != 'FORBIDDEN' or decision.get('legacy_engine') != 'INVALIDATED' or decision.get('valid_engine') != 'P2296C_REAL_EXIT_ENGINE' or not REQUIRED_RESTRICTIONS.issubset(set(decision.get('restrictions', []))):
        raise ValueError('P2298_UNSAFE_DECISION')
    signatures = set()
    for item in candidates:
        if not isinstance(item, dict) or item.get('mode') != 'PAPER_ONLY' or item.get('real_orders') != 'FORBIDDEN' or item.get('final_status') != 'FINAL_APPROVED' or item.get('symbol') != 'GER40' or item.get('timeframe') != 'H1':
            raise ValueError('P2298_UNAUTHORIZED_CANDIDATE')
        metrics = tuple(item.get(f'seg{k}_pf') for k in range(1, 5))
        if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x < 0 for x in metrics):
            raise ValueError('P2298_INVALID_METRICS')
        if item.get('segments_passed') != sum(x >= 1.15 for x in metrics):
            raise ValueError('P2298_INCONSISTENT_SEGMENTS')
        signatures.add(metrics)
    return {'status': 'PAPER_WATCH_ONLY_NOT_CERTIFIED', 'candidates': len(candidates), 'distinct_metric_signatures': len(signatures), 'independent_edges_certified': 0, 'real_orders': 'FORBIDDEN', 'ftmo_real': 'FORBIDDEN', 'e2e_certified': False}
