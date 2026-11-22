"""P2303 offline-only MT5 bridge evidence audit. Never reads/writes terminal paths."""
def audit_consumption(record, logs):
    if not isinstance(record, dict) or not isinstance(logs, (list,tuple)):
        raise ValueError("P2303_INVALID_INPUT")
    if any(record.get(k)!=v for k,v in {"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","consumption_status":"PENDING_MT5_CONSUMPTION"}.items()):
        raise ValueError("P2303_UNSAFE_RECORD")
    if str(record.get("exists_now")) not in ("True","true", "1"):
        raise ValueError("P2303_MISSING_ORDER_FILE")
    if not isinstance(record.get("selected_signal_id"),str) or not record["selected_signal_id"].startswith("P2302_"):
        raise ValueError("P2303_INVALID_SIGNAL_ID")
    content=record.get("content_now")
    if not isinstance(content,str) or content.split(",")[:4]!=[record.get("selected_symbol"),record.get("selected_action"),str(record.get("selected_lot")),record["selected_signal_id"]]:
        raise ValueError("P2303_CONTENT_MISMATCH")
    confirmed=[]
    for log in logs:
        if not isinstance(log,dict):
            raise ValueError("P2303_INVALID_LOG")
        if str(log.get("contains_signal_id")).lower()=="true":
            confirmed.append(log)
    return {"status":"MT5_CONSUMPTION_NOT_CERTIFIED","file_exists":True,"logs_checked":len(logs),
            "matching_log_metadata":len(confirmed),"terminal_read_proven":False,
            "demo_fill_proven":False,"orders_authorized":0,"e2e_certified":False}
