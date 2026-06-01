from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from app.embeddings_internal import embed_text_internal, embed_batch_internal

router = APIRouter()


class EmbedRequest(BaseModel):
    text: str = Field(..., description="Texto a ser convertido em embedding interno")
    model: str | None = Field(default=None, description="Nome lógico do modelo interno")


class BatchEmbedRequest(BaseModel):
    texts: List[str] = Field(..., description="Lista de textos para embedding interno")
    model: str | None = Field(default=None, description="Nome lógico do modelo interno")


@router.post("/embeddings/internal/embed")
async def embeddings_internal_embed(req: EmbedRequest):
    result = embed_text_internal(req.text, req.model)
    return result


@router.post("/embeddings/internal/embed-batch")
async def embeddings_internal_embed_batch(req: BatchEmbedRequest):
    result = embed_batch_internal(req.texts, req.model)
    return result
