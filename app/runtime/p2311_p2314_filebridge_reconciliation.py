"""Reconcile P2311-P2314 MT5 FileBridge history without touching a terminal.

Installation, file existence and generic log hits are not consumption receipts.
"""
def reconcile_filebridge(install, reopen, forward, audit):
    for item in (install,reopen,forward,audit):
        if not isinstance(item,dict):
            raise ValueError("FILEBRIDGE_INVALID_EVIDENCE")
    if install.get("mode")!="PAPER_ONLY" or install.get("real_orders")!="FORBIDDEN":
        raise ValueError("FILEBRIDGE_UNSAFE_INSTALL")
    if reopen.get("paper_forward")!="REOPENED" or reopen.get("p2310_blocker")!="MT5_FILEBRIDGE_PENDING_CONSUMPTION":
        raise ValueError("FILEBRIDGE_INVALID_REOPEN")
    if forward.get("write_status")!="SKIPPED_PENDING_SIGNAL_EXISTS" or forward.get("previous_signal_exists")!="True":
        raise ValueError("FILEBRIDGE_UNVERIFIED_FORWARD")
    if audit.get("consumption_status")!="PENDING_AFTER_PARSE_OR_NOT_DELETED" or audit.get("signal_exists")!="True":
        raise ValueError("FILEBRIDGE_UNVERIFIED_CONSUMPTION")
    if audit.get("mode")!="PAPER_ONLY" or audit.get("real_orders")!="FORBIDDEN" or audit.get("ftmo_real")!="FORBIDDEN":
        raise ValueError("FILEBRIDGE_UNSAFE_AUDIT")
    previous=forward.get("previous_content")
    observed=audit.get("signal_content")
    if not isinstance(previous,str) or not previous or previous!=observed:
        raise ValueError("FILEBRIDGE_SIGNAL_MISMATCH")
    parts=observed.split(",")
    if len(parts)!=5 or parts[:4]!=["GER40","BUY","0.01","P2311_ACTIVE_TEST"]:
        raise ValueError("FILEBRIDGE_SIGNAL_INVALID")
    return {"status":"MT5_CONSUMPTION_UNVERIFIED","historical_reopen":"REOPENED",
            "historical_resolved_claim_overridden":True,
            "terminal_read_proven":False,"broker_fill_proven":False,
            "stale_signal_present":True,"signal_authorized":False,
            "orders_authorized":0,"e2e_certified":False}
