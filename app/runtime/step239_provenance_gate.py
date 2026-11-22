"""STEP239 documentary provenance cannot be promoted to executable capability."""
def assess_step239(steps_record, missing_inventory):
    if not isinstance(steps_record,dict) or steps_record.get('step') != 239:
        raise ValueError('STEP239 identity required')
    if not isinstance(missing_inventory,str):
        raise ValueError('inventory text required')
    missing='STEP239' in {line.strip() for line in missing_inventory.splitlines()}
    if steps_record.get('status') == 'unknown' and missing:
        return {'step_id':239,'state':'HISTORICAL_UNKNOWN_AND_MISSING','certified':False}
    return {'step_id':239,'state':'CONFLICT_OR_UNVERIFIED','certified':False}
