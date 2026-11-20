"""P1300+P1350 chronological offline integration, no broker."""
from .p1300_validator import validate
from .p1350_regime_classifier import classify

def run(bars, *, historical_source_sha256=None, **costs):
    validation=validate(bars,**costs)
    regime=classify(bars)
    if validation['source_sha256'] != regime['source_sha256']:
        raise ValueError('OHLC source mismatch')
    if historical_source_sha256 is not None and historical_source_sha256 != validation['source_sha256']:
        raise ValueError('historical source hash mismatch')
    return {'status':'OFFLINE_ONLY','p1300':validation,'p1350':regime,
            'historical_source_verified':historical_source_sha256 is not None,
            'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
