def reconcile(write, audit):
    if not isinstance(write, dict) or not isinstance(audit, dict):
        raise ValueError('INVALID_EVIDENCE')
    for x in (write,audit):
        if x.get('mode') != 'PAPER_ONLY' or x.get('real_orders') != 'FORBIDDEN' or x.get('ftmo_real') != 'FORBIDDEN':
            raise ValueError('UNSAFE_MODE')
    if write.get('exists_after_write') != 'True' or audit.get('signal_exists') != 'True':
        raise ValueError('UNEXPECTED_FILE_STATE')
    if write.get('order_line') != audit.get('signal_content'):
        raise ValueError('SIGNAL_IDENTITY_MISMATCH')
    parts = write['order_line'].split(',')
    if len(parts) != 5 or parts[:4] != ['GER40','BUY','0.01','P2316_34f0bb1186de']:
        raise ValueError('UNEXPECTED_SIGNAL')
    if audit.get('consumption_status') != 'PARSED_BUT_FILE_STILL_PRESENT':
        raise ValueError('UNVERIFIED_CONSUMPTION_STATE')
    return {'status':'P2317_UNCONSUMED_FILE', 'signal_id':parts[3], 'terminal_read_proven':False, 'file_cleared':False, 'orders_authorized':0, 'e2e_certified':False}
