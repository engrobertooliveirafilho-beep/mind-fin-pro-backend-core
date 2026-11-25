def summarize(corpus):
    if not isinstance(corpus, list) or not corpus:
        return {'status':'blocked','reason':'EMPTY_OR_INVALID_CORPUS'}
    counts = dict.fromkeys(('planejado','em_andamento','concluido','desconhecido'),0)
    for item in corpus:
        if not isinstance(item,dict):
            return {'status':'blocked','reason':'INVALID_RECORD'}
        state=item.get('status_planejamento')
        counts[state if isinstance(state,str) and state in counts else 'desconhecido'] += 1
    return {'status':'partial' if counts['desconhecido'] else 'ok','total_registros':len(corpus),'status_planejamento':counts}
