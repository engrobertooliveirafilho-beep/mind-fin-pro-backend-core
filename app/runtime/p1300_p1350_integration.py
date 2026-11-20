"""P1300+P1350 offline integration: fit regime on training data only."""
from .p1300_validator import validate
from .p1350_regime_classifier import classify

def run(bars, *, historical_source_sha256=None, **costs):
    validation = validate(bars, **costs)
    training_count = validation['train_bars']
    if training_count < 20:
        raise ValueError('P1350 requires at least 20 training bars')
    regime = classify(bars[:training_count], min_bars=training_count)
    if historical_source_sha256 is not None and historical_source_sha256 != validation['source_sha256']:
        raise ValueError('historical source hash mismatch')
    return {'status':'OFFLINE_ONLY', 'p1300':validation, 'p1350':regime,
            'regime_fit_scope':'TRAIN_ONLY', 'regime_fit_bars':training_count,
            'full_source_sha256':validation['source_sha256'],
            'training_source_sha256':regime['source_sha256'],
            'historical_source_verified':historical_source_sha256 is not None,
            'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
