"""Fail-closed evidence gate for PAPER-only trader; no order placement."""
from dataclasses import dataclass
from typing import Mapping
REQUIRED=('canonical_runtime_hash_verified','all_motors_reconciled','end_to_end_integration_pass','ftmo_rules_current_verified','historical_oos_pass','forward_demo_30_90d_pass','broker_costs_verified','daily_and_total_loss_guard_verified','explicit_human_authorization')
@dataclass(frozen=True)
class GateResult:
    paper_technical_tests: bool
    release_authorized: bool
    missing: tuple
    real_orders: int=0
def assess(evidence:Mapping[str,bool],*,paper_tests_pass:bool)->GateResult:
    if set(evidence)-set(REQUIRED): raise ValueError('unknown evidence key')
    if any(type(v) is not bool for v in evidence.values()): raise TypeError('evidence must be explicit booleans')
    missing=tuple(k for k in REQUIRED if evidence.get(k) is not True)
    return GateResult(bool(paper_tests_pass),bool(paper_tests_pass) and not missing,missing)
