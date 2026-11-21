"""STEP456: validate and plan modality routing; no processing or network calls."""

class RoutingRejected(ValueError):
    pass

PIPELINES = {'text': 'nlp_core', 'audio': 'audio_asr', 'video': 'video_vision', 'three_d': 'three_d_engine'}

def plan_routes(session_id, channels):
    if not isinstance(session_id, str) or not session_id.strip():
        raise RoutingRejected('session_id required')
    if not isinstance(channels, list) or not channels:
        raise RoutingRejected('nonempty channels required')
    if len(channels) > 100:
        raise RoutingRejected('channel limit exceeded')
    seen = set()
    routes = []
    for ch in channels:
        if not isinstance(ch, dict):
            raise RoutingRejected('invalid channel')
        cid, modality, size, priority = (ch.get(k) for k in ('channel_id', 'modality', 'size_bytes', 'priority'))
        if not isinstance(cid, str) or not cid.strip() or cid in seen:
            raise RoutingRejected('invalid or duplicate channel_id')
        if modality not in PIPELINES:
            raise RoutingRejected('unsupported modality')
        if isinstance(size, bool) or not isinstance(size, int) or not 0 <= size <= 100_000_000:
            raise RoutingRejected('invalid size')
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 10:
            raise RoutingRejected('invalid priority')
        seen.add(cid)
        routes.append({'channel_id': cid, 'modality': modality, 'pipeline': PIPELINES[modality], 'priority': priority, 'status': 'PLANNED_NOT_EXECUTED'})
    return {'session_id': session_id, 'routes': routes, 'executed': False}
