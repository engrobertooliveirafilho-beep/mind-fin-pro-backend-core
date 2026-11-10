"""ET665.R311: offline-only P2404 integration, pinned source bytes before CSV parsing.
No external I/O except reading explicitly supplied local files; no runtime or certification.
"""
import csv
import json
from pathlib import Path
from .et665_r305_pinned_authority_gate import verify_pinned_manifest
from .et665_r309_pure_correlation import analyze_paper_series
from .et665_r315_immutable_csv_snapshot import snapshot_verified_csv

QUARANTINED=frozenset({"de40_cycle_events.csv","p2403b_edge_trade_series.csv",
                       "p2403e_de40_edge_trade_series.csv"})
EXPECTED=("edge_id","timestamp","pnl_r")
MAX_ROWS=100_000

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
    # A pinned hash proves byte integrity, not independent provenance. Reject
    # historical generators by manifest metadata, even after file renaming.
    try:
        entry=json.loads(Path(manifest).read_text(encoding="utf-8"))["sources"][source_id]
        generator=str(entry.get("generator","")).lower()
        lineage=str(entry.get("lineage","")).lower()
        if any(token in generator+" "+lineage for token in ("p2403e","sha256_stride","hash_scheduled","synthetic_entry")):
            result["issues"]=["NONCAUSAL_GENERATOR_QUARANTINED"]
            return result
        if not isinstance(entry.get("generator"),str) or not entry["generator"].strip() or not isinstance(entry.get("lineage"),str) or not entry["lineage"].strip():
            result["issues"]=["GENERATOR_LINEAGE_REQUIRED"]
            return result
        if entry.get("independent_review") is not True:
            result["issues"]=["INDEPENDENT_REVIEW_REQUIRED"]
            return result
    except (OSError,ValueError,TypeError,KeyError,UnicodeError):
        result["issues"]=["PROVENANCE_METADATA_INVALID"]
        return result
    # Parse the exact verified byte snapshot, not a second read of source.
    snapshot=snapshot_verified_csv(source,entry["sha256"])
    if not snapshot["verified"]:
        result["issues"]=["MALFORMED_CSV"] if snapshot["issues"]==["INVALID_CSV_ROWS"] else snapshot["issues"]
        return result
    rows=[]
    for index,row in enumerate(snapshot["rows"],1):
        if index>MAX_ROWS:
            result["issues"]=["ROW_LIMIT_EXCEEDED"]
            return result
        try:
            pnl=float(row["pnl_r"])
        except (ValueError,TypeError):
            result["issues"]=["INVALID_PNL"]
            return result
        rows.append({"edge_id":row["edge_id"],"timestamp":row["timestamp"],"pnl_r":pnl})
    try:
        analysis=analyze_paper_series(rows)
        result.update({"issues":analysis["issues"],"pairs":analysis["pairs"],
                       "analysis_valid":analysis["analysis_valid"]})
    except (OSError,UnicodeError,csv.Error,ValueError):
        result["issues"]=["CSV_UNREADABLE_OR_MALFORMED"]
    return result
