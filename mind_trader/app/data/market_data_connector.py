import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.data.ingestion_adapters import ingest_with_quality_gate, checksum
from mind_trader.app.data.data_catalog import register_dataset
from mind_trader.app.data.dataset_lineage import create_dataset_lineage

SUPPORTED_SOURCES={"MT5_CSV","PROFIT_CSV","GENERIC_OHLCV_CSV"}

def market_data_connector(source_type, file_path, symbol, timeframe, db_path="mind_trader/data/market.sqlite", catalog_path="mind_trader/reports/P8.61_data_catalog.json", lineage_path="mind_trader/reports/P8.64_dataset_lineage.json"):
    if source_type not in SUPPORTED_SOURCES:
        return {"decision":"BLOCKED_UNSUPPORTED_SOURCE","source_type":source_type,"production":"BLOCKED","edge_claim":"NONE"}

    p=Path(file_path)
    if not p.exists():
        return {"decision":"BLOCKED_FILE_NOT_FOUND","file_path":str(file_path),"production":"BLOCKED","edge_claim":"NONE"}

    dataset=None
    lineage=None

    try:
        result=ingest_with_quality_gate(p,symbol,timeframe,db_path)
    except Exception as e:
        result={
            "decision":"DATA_BLOCKED",
            "reason":"INGESTION_EXCEPTION",
            "error":str(e),
            "source":str(p),
            "quality":{"rows":0,"quality_passed":False}
        }

    base_manifest={
        "file_path":str(p),
        "file_checksum":checksum(p),
        "db_path":db_path,
        "ingestion_result":result
    }

    if result["decision"]=="INGESTED_AND_BACKTEST_ALLOWED":
        q=result["quality"]
        dataset=register_dataset(
            symbol=symbol,
            timeframe=timeframe,
            source_hash=checksum(p),
            rows=q["rows"],
            quality_passed=q["quality_passed"],
            path=catalog_path
        )
        if dataset["status"]=="APPROVED_FOR_RESEARCH":
            lineage=create_dataset_lineage(dataset,base_manifest,lineage_path)
            dataset["lineage_hash"]=lineage["lineage_hash"]

    manifest={
        "connector":"P8.65_MARKET_DATA_CONNECTOR_WITH_CATALOG_AND_LINEAGE",
        "source_type":source_type,
        "file_path":str(p),
        "file_checksum":checksum(p),
        "symbol":symbol,
        "timeframe":timeframe,
        "db_path":db_path,
        "catalog_path":catalog_path,
        "lineage_path":lineage_path,
        "dataset":dataset,
        "dataset_id":dataset.get("dataset_id") if dataset else None,
        "lineage":lineage,
        "lineage_hash":lineage.get("lineage_hash") if lineage else None,
        "ingestion_result":result,
        "created_at":datetime.now(UTC).isoformat(),
        "decision":"DATA_CONNECTED_CATALOGED_LINEAGED" if dataset and lineage else "DATA_BLOCKED",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.65_market_data_connector_lineage_manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )

    return manifest
