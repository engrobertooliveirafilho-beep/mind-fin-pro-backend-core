"""ET665.R451: strict historical paper-signal boundary; no execution interface."""
from collections.abc import Mapping

def admit_paper_signal(row):
    if not isinstance(row, Mapping): return False, 'INVALID_INPUT'
    if row.get('mode') != 'PAPER_ONLY' or row.get('real_orders') != 'FORBIDDEN' or row.get('ftmo_real') != 'FORBIDDEN':
        return False, 'UNSAFE_MODE'
    if row.get('execution_filter_decision') != 'ALLOW_PAPER' or row.get('paper_permission') != 'ALLOW':
        return False, 'BLOCKED_BY_POLICY'
    if row.get('fidelity_passed') not in ('True', True): return False, 'FIDELITY_NOT_PROVEN'
    if row.get('warning') != 'THIS_IS_NOT_A_REAL_ORDER': return False, 'WARNING_MISSING'
    if not row.get('time') or not row.get('cycle_transition'): return False, 'MISSING_CONTEXT'
    if row.get('next_close') not in ('', None) or row.get('realized_r') not in ('', None):
        return False, 'FUTURE_OUTCOME_PRESENT'
    return True, 'PAPER_RESEARCH_ONLY'
