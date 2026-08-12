import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.data.market_data_connector import market_data_connector

def infer_source_type(path):
    name=Path(path).name.lower()
    if "mt5" in name: return "MT5_CSV"
    if "profit" in name: return "PROFIT_CSV"
    return "GENERIC_OHLCV_CSV"

def batch_ingest_market_folder(folder, symbol, timeframe, db_path="mind_trader/data/market.sqlite"):
    folder=Path(folder)
    if not folder.exists():
        return {"decision":"BATCH_BLOCKED_FOLDER_NOT_FOUND","production":"BLOCKED","edge_claim":"NONE"}

    files=sorted([p for p in folder.glob("*.csv")])
    results=[]

    for f in files:
        try:
            results.append(market_data_connector(infer_source_type(f),f,symbol,timeframe,db_path))
        except Exception as e:
            results.append({
                "decision":"DATA_BLOCKED",
                "reason":"INGESTION_EXCEPTION",
                "error":str(e),
                "file_path":str(f),
                "source_type":infer_source_type(f),
                "production":"BLOCKED",
                "edge_claim":"NONE"
            })

    manifest={
        "batch":"P8.60_BATCH_MARKET_DATA_INGESTION",
        "created_at":datetime.now(UTC).isoformat(),
        "folder":str(folder),
        "files_found":len(files),
        "connected":sum(1 for r in results if r.get("decision") in ["DATA_CONNECTED","DATA_CONNECTED_AND_CATALOGED","DATA_CONNECTED_CATALOGED_LINEAGED"]),
        "blocked":sum(1 for r in results if r.get("decision") not in ["DATA_CONNECTED","DATA_CONNECTED_AND_CATALOGED","DATA_CONNECTED_CATALOGED_LINEAGED"]),
        "results":results,
        "decision":"BATCH_COMPLETED" if files else "BATCH_EMPTY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.60_batch_market_ingestion_manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )

    return manifest



