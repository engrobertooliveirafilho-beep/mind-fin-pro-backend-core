"""Fail-closed PAPER evidence gate recovered from Drive V7.

Source Drive file: 1vyprf9epfAQ-w8oyfyPU0t04U3jV1qK7.
No broker connection. Release authorization is a documentary gate result,
not permission to place real orders.
"""
from dataclasses import dataclass
from typing import Mapping

REQUIRED = (
    'canonical_runtime_hash_verified',
    'all_motors_reconciled',
    'end_to_end_integration_pass',
    'ftmo_rules_current_verified',
    'historical_oos_pass',
    'forward_demo_30_90d_pass',
    'broker_costs_verified',
    'daily_and_total_loss_guard_verified',
    'explicit_human_authorization',
)

@dataclass(frozen=True)
class GateResult:
    paper_technical_tests: bool
    release_authorized: bool
    missing: tuple
    real_orders: int = 0

def assess(evidence: Mapping[str, bool], *, paper_tests_pass: bool) -> GateResult:
    if not isinstance(evidence, Mapping):
        raise TypeError('evidence must be a mapping')
    if type(paper_tests_pass) is not bool:
        raise TypeError('paper_tests_pass must be an explicit boolean')
    if set(evidence) - set(REQUIRED):
        raise ValueError('unknown evidence key')
    if any(type(value) is not bool for value in evidence.values()):
        raise TypeError('evidence must be explicit booleans')
    missing = tuple(key for key in REQUIRED if evidence.get(key) is not True)
    return GateResult(paper_tests_pass, paper_tests_pass and not missing, missing)
