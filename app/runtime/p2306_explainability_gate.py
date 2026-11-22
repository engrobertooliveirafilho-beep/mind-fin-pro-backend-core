"""P2306: explanation must not override missing market or execution evidence."""
def reconcile_explainability(row, *, feature_evidence=None):
    if not isinstance(row,dict):
        raise ValueError("P2306_INVALID_ROW")
    required={"symbol":"GER40","timeframe":"H1","action":"BUY",
              "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
              "consumption_status":"PENDING_MT5_CONSUMPTION"}
    if any(row.get(k)!=v for k,v in required.items()):
        raise ValueError("P2306_UNSAFE_EVIDENCE")
    if not isinstance(row.get("signal_id"),str) or not row["signal_id"].startswith("P2302_"):
        raise ValueError("P2306_INVALID_SIGNAL_ID")
    try:
        confidence=int(row["confidence_score"])
    except (KeyError,TypeError,ValueError):
        raise ValueError("P2306_INVALID_CONFIDENCE") from None
    if not 0<=confidence<=100:
        raise ValueError("P2306_INVALID_CONFIDENCE")
    unknown_regime=str(row.get("regime","")).startswith("UNKNOWN_")
    unknown_session=str(row.get("session","")).startswith("UNKNOWN_")
    if not row.get("regime") or not row.get("session"):
        raise ValueError("P2306_MISSING_CONTEXT")
    # A confidence score is an annotation, not independently sourced feature proof.
    return {"status":"EXPLANATION_INSUFFICIENT_BLOCK",
            "historical_decision":row.get("status"),"confidence_annotation":confidence,
            "unknown_regime":unknown_regime,"unknown_session":unknown_session,
            "feature_provenance_verified":False,"consumption_verified":False,
            "signal_authorized":False,"orders_authorized":0,"e2e_certified":False}
