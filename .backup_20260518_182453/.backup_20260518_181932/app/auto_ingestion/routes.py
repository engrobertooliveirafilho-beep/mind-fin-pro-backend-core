from fastapi import APIRouter
from app.auto_ingestion.runtime import AutoIngestionRuntime

router=APIRouter()

@router.post("/admin/auto-ingestion/item")
def ingest_item(payload:dict):
    return AutoIngestionRuntime().ingest(payload)

@router.post("/admin/auto-ingestion/batch")
def ingest_batch(payload:dict):
    return AutoIngestionRuntime().batch(payload.get("items",[]))
