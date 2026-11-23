"""Fail-closed documentary approval gate for STEP planning, no I/O."""

def authorize(step_id, records):
    blocked = {'status': 'blocked', 'approved': False, 'executed': False, 'e2e_certified': False}
    if type(step_id) is not int or step_id < 1 or type(records) is not list or len(records) > 10000:
        return {**blocked, 'reason': 'invalid_input'}
    found = []
    for record in records:
        if type(record) is not dict or type(record.get('step_number')) is not int:
            return {**blocked, 'reason': 'invalid_record'}
        if record['step_number'] == step_id:
            found.append(record)
    if len(found) != 1:
        return {**blocked, 'reason': 'missing_or_ambiguous_step'}
    record = found[0]
    if record.get('status') != 'aprovado' or record.get('status_dev') != 'validado' or record.get('status_prod') != 'validado':
        return {**blocked, 'reason': 'insufficient_documentary_approval'}
    # A status field is not a signed certificate: explicit provenance is mandatory.
    if type(record.get('approval_evidence')) is not str or not record['approval_evidence'].startswith('sha256:') or len(record['approval_evidence']) != 71:
        return {**blocked, 'reason': 'missing_provenance'}
    return {'status': 'documentary_candidate_only', 'approved': False, 'executed': False, 'e2e_certified': False, 'reason': 'external_evidence_verification_required'}
