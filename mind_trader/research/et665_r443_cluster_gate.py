"""Fail-closed validation for research-only P2393 cluster evidence."""
from collections.abc import Mapping

def validate_cluster(cluster, members, evidence):
    if not isinstance(cluster, Mapping) or not isinstance(evidence, Mapping) or not isinstance(members, list):
        return False, 'INVALID_INPUT'
    if evidence.get('mode') != 'PAPER_ONLY' or evidence.get('real_execution_allowed') is not False:
        return False, 'SAFETY_LOCK'
    if evidence.get('source_type') != 'EMPIRICAL_TRADES' or evidence.get('independent_validation') is not True:
        return False, 'NO_EMPIRICAL_PROOF'
    if len(members) < 2 or len({m.get('candidate_id') for m in members if isinstance(m, Mapping)}) != len(members):
        return False, 'INSUFFICIENT_UNIQUE_MEMBERS'
    if not all(isinstance(m, Mapping) and m.get('empirical_certified') is True and m.get('trade_series_sha256') for m in members):
        return False, 'MEMBER_UNVERIFIED'
    if cluster.get('decision') != 'PROMOTE_CLUSTER':
        return False, 'NOT_PROMOTED'
    return True, 'RESEARCH_ELIGIBLE_ONLY'
