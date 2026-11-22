"""Independent reconciliation of P2310 historical module claims."""

REQUIRED = {
    'monte_carlo': 'P2300_PASS_4_OF_4',
    'spread_slippage_stress': 'P2301_PASS_4_OF_4',
    'mt5_consumption': 'PENDING_MT5_CONSUMPTION',
    'paper_watch_portfolio': '7 rows / 4 symbols / PASS_MINIMUM_SYMBOL_DIVERSIFICATION',
}

def reconcile_snapshot(summary, capacity, blockers):
    if not all(isinstance(x, dict) for x in (summary, capacity, blockers)):
        raise ValueError('P2310_INVALID_INPUT')
    if summary.get('real_orders') != 'FORBIDDEN' or summary.get('ftmo_real') != 'FORBIDDEN':
        raise ValueError('P2310_UNSAFE_MODE')
    if capacity.get('mode') != 'PAPER_ONLY' or capacity.get('real_orders') != 'FORBIDDEN' or capacity.get('ftmo_real') != 'FORBIDDEN':
        raise ValueError('P2310_UNSAFE_CAPACITY')
    if any(capacity.get(k) != v for k, v in REQUIRED.items()):
        raise ValueError('P2310_MISSING_HISTORICAL_EVIDENCE')
    if blockers.get('MT5_FILEBRIDGE_PENDING_CONSUMPTION') != 'OPEN':
        raise ValueError('P2310_BLOCKER_MISMATCH')
    if summary.get('mt5_consumption_status') != 'PENDING_MT5_CONSUMPTION':
        raise ValueError('P2310_CONSUMPTION_MISMATCH')
    return {'status':'SNAPSHOT_INVENTORY_ONLY', 'modules_historically_reported':12,
            'mt5_consumption_certified':False, 'monte_carlo_certified':False,
            'stress_certified':False, 'diversification_certified':False,
            'orders_authorized':0, 'e2e_certified':False}
