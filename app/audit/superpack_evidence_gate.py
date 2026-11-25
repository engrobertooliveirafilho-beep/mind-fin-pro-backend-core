def assess(required, evidence):
    if not required or len(set(required)) != len(required):
        raise ValueError('invalid requirements')
    missing = [key for key in required if evidence.get(key) is not True]
    return {'status': 'blocked' if missing else 'evidence_present', 'missing': missing, 'certified': False}
