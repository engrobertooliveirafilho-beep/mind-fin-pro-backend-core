"""ET665.R311: offline-only P2404 integration, pinned source bytes before CSV parsing.
No external I/O except reading explicitly supplied local files; no runtime or certification.
"""
import csv
from pathlib import Path
from .et665_r305_pinned_authority_gate import verify_pinned_manifest
from .et665_r309_pure_correlation import analyze_paper_series

QUARANTINED=frozenset({"de40_cycle_events.csv","p2403b_edge_trade_series.csv",
                       "p2403e_de40_edge_trade_series.csv"})
EXPECTED=("edge_id","timestamp","pnl_r")

def analyze_verified_paper_csv(source, manifest, trusted_manifest_sha256, *, source_id):
    result={"status":"QUARANTINE","issues":[],"analysis_valid":False,
            "authority_integrity_verified":False,"source_integrity_verified":False,
            "causal_signal_verified":False,"correlation_certified":False,
            "runtime_promotion_allowed":False,"pairs":[]}
    if not isinstance(source,(str,Path)):
        result["issues"]=["INVALID_SOURCE"]
        return result
    if Path(source).name.lower() in QUARANTINED:
        result["issues"]=["HISTORICAL_SOURCE_QUARANTINED"]
        return result
    checked=verify_pinned_manifest(source,manifest,trusted_manifest_sha256,source_id=source_id)
    result["authority_integrity_verified"]=checked["authority_integrity_verified"]
    result["source_integrity_verified"]=checked["source_integrity_verified"]
    if not checked["source_integrity_verified"]:
        result["issues"]=checked["issues"]
        return result
    try:
        with Path(source).open("r",encoding="utf-8-sig",newline="") as handle:
            reader=csv.DictReader(handle,strict=True)
            if reader.fieldnames is None or tuple(reader.fieldnames)!=EXPECTED:
                result["issues"]=["INVALID_CSV_SCHEMA"]
                return result
            rows=[]
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    result["issues"]=["MALFORMED_CSV"]
                    return result
                try:
                    pnl=float(row["pnl_r"])
                except (ValueError,TypeError):
                    result["issues"]=["INVALID_PNL"]
                    return result
                rows.append({"edge_id":row["edge_id"],"timestamp":row["timestamp"],"pnl_r":pnl})
        analysis=analyze_paper_series(rows)
        result.update({"issues":analysis["issues"],"pairs":analysis["pairs"],
                       "analysis_valid":analysis["analysis_valid"]})
    except (OSError,UnicodeError,csv.Error,ValueError):
        result["issues"]=["CSV_UNREADABLE_OR_MALFORMED"]
    return result
