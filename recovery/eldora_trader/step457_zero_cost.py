"""STEP457 zero-cost GPU policy. Never provisions, scales or calls providers."""
class ScalingRejected(ValueError):
    pass

def evaluate_gpu_scaling(*, queue_length, current_instances, requested_instances, cost_limit_brl=0):
    for name, value in [('queue_length',queue_length),('current_instances',current_instances),('requested_instances',requested_instances)]:
        if isinstance(value,bool) or not isinstance(value,int) or value < 0:
            raise ScalingRejected('invalid '+name)
    if isinstance(cost_limit_brl,bool) or not isinstance(cost_limit_brl,(int,float)) or cost_limit_brl != 0:
        raise ScalingRejected('zero-cost policy required')
    if requested_instances > current_instances:
        raise ScalingRejected('GPU provisioning forbidden under zero-cost policy')
    return {'queue_length':queue_length,'current_instances':current_instances,'requested_instances':requested_instances,'authorized_to_execute':False,'action':'NO_OP','reason':'PAPER_ONLY_ZERO_COST'}
