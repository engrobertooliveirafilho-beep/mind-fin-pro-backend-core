import hashlib

def review(raw, inventory, danger=False):
    digest = hashlib.sha256(raw).hexdigest()
    valid = inventory.get('sha256') == digest and inventory.get('status') == 'STATIC_INVENTORY_ONLY'
    return {'sha256': digest, 'action': 'REVIEW_OR_QUARANTINE' if danger or not valid else 'TEST_CANDIDATE', 'promotion_allowed': False, 'real_execution_allowed': False}
