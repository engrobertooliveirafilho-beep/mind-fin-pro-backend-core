"""P2383 chronological walk-forward contract.

The 227 P2382 survivors are selection-contaminated and MUST NOT be the test population.
Use the complete 500-row P2380 feedback population. This module splits data only;
it does not claim performance or promote strategies.
"""
from datetime import datetime

REQUIRED_MODE = "PAPER_ONLY"
REQUIRED_FORBIDDEN = "FORBIDDEN"
REQUIRED_WARNING = "PAPER_FEEDBACK_PROXY_NOT_REAL_PNL"

REQUIRED=500

def _parse_time(value):
    for fmt in ("%Y.%m.%d %H:%M:%S","%Y-%m-%d %H:%M:%S","%Y-%m-%dT%H:%M:%S"):
        try:return datetime.strptime(value,fmt)
        except (TypeError,ValueError):pass
    raise ValueError("P2383_INVALID_ENTRY_TIME")

def chronological_folds(rows, *, source_mission, test_windows=5, initial_train_fraction=0.5):
    if source_mission!="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING":
        raise ValueError("P2383_WRONG_SOURCE_POPULATION")
    if not isinstance(rows,list) or len(rows)!=REQUIRED:
        raise ValueError("P2383_REQUIRES_COMPLETE_500_ROW_POPULATION")
    if test_windows!=5 or initial_train_fraction!=0.5:
        raise ValueError("P2383_POLICY_MISMATCH")
    seen=set(); normalized=[]; safety_presence=set()
    for row in rows:
        if (not isinstance(row,dict) or type(row.get("signal_id")) is not str
                or not row["signal_id"].strip() or row["signal_id"] in seen):
            raise ValueError("P2383_DUPLICATE_OR_MISSING_SIGNAL_ID")
        seen.add(row["signal_id"])
        # Fail closed for the canonical Drive feedback schema. Legacy synthetic
        # unit fixtures without safety metadata remain supported, but any
        # partial metadata must be rejected rather than silently accepted.
        safety = ("mode", "real_orders", "ftmo_real", "warning")
        present = [name for name in safety if name in row]
        safety_presence.add(bool(present))
        if present and len(present) != len(safety):
            raise ValueError("P2383_INCOMPLETE_PAPER_SAFETY_METADATA")
        if present and (row["mode"] != REQUIRED_MODE
                        or row["real_orders"] != REQUIRED_FORBIDDEN
                        or row["ftmo_real"] != REQUIRED_FORBIDDEN
                        or row["warning"] != REQUIRED_WARNING):
            raise ValueError("P2383_UNSAFE_OR_NONPROXY_FEEDBACK")
        if "realized_r" not in row or not row.get("entry_time"):
            raise ValueError("P2383_MISSING_OUTCOME_OR_TIME")
        try: realized=float(row["realized_r"])
        except (TypeError,ValueError): raise ValueError("P2383_INVALID_REALIZED_R") from None
        if realized!=realized or realized in (float("inf"),float("-inf")):
            raise ValueError("P2383_INVALID_REALIZED_R")
        normalized.append((_parse_time(row["entry_time"]),row))
    if len(safety_presence) != 1:
        raise ValueError("P2383_MIXED_PAPER_SAFETY_SCHEMA")
    normalized.sort(key=lambda item:(item[0],item[1]["signal_id"]))
    if len({t for t,_ in normalized})<test_windows+1:
        raise ValueError("P2383_INSUFFICIENT_TIME_POINTS")
    n=len(normalized); train_end=int(n*initial_train_fraction)
    remaining=n-train_end
    if remaining<test_windows:
        raise ValueError("P2383_INSUFFICIENT_TEST_ROWS")
    # Never split rows sharing a timestamp across train/test or test/test.
    # Equal-time records have no defensible ordering for causal learning.
    boundaries = [train_end + (remaining * k) // test_windows
                  for k in range(test_windows)] + [n]
    for pos in boundaries[:-1]:
        if normalized[pos - 1][0] >= normalized[pos][0]:
            raise ValueError("P2383_TEMPORAL_TIE_AT_FOLD_BOUNDARY")
    folds=[]
    for k in range(test_windows):
        start=train_end+(remaining*k)//test_windows
        end=train_end+(remaining*(k+1))//test_windows
        train=[row for _,row in normalized[:start]]
        test=[row for _,row in normalized[start:end]]
        if not train or not test or _parse_time(train[-1]["entry_time"])>=_parse_time(test[0]["entry_time"]):
            raise ValueError("P2383_TEMPORAL_LEAKAGE")
        folds.append({"fold":k+1,"train_rows":train,"test_rows":test,
                      "train_end":train[-1]["entry_time"],"test_start":test[0]["entry_time"],
                      "test_end":test[-1]["entry_time"]})
    return {"status":"CHRONOLOGICAL_SPLIT_READY_NOT_PERFORMANCE_CERTIFIED",
            "source_rows":n,"initial_train_rows":train_end,"folds":folds,
            "p2382_survivors_allowed_as_primary_input":False,
            "performance_certified":False,"promotion_allowed":False}
