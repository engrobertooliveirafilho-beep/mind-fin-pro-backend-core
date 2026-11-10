from datetime import datetime
from typing import List, Dict, Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
router = APIRouter()
SearchMode = Literal["web_stub", "internal", "hybrid"]
class ResearchQuery(BaseModel):
    query: str
    max_results: int = Field(5, ge=1, le=20)
    mode: SearchMode = "web_stub"
class ResearchResult(BaseModel):
    rank: int
    title: str
    snippet: str
    source: str
    score: float
class ResearchResponse(BaseModel):
    query: str
    mode: SearchMode
    results: List[ResearchResult]
    meta: Dict[str, Any]
def _make_stub_results(query: str, max_results: int, mode: SearchMode) -> List[ResearchResult]:
    base_tokens=[t for t in query.split() if t.strip()]
    joined=" ".join(base_tokens) or "MIND"
    results=[]
    for i in range(1,max_results+1):
        score=round(1.0-(i-1)*0.07,3)
        if score<0.3: score=0.3
        title=f"[{mode}] insight {i} sobre '{joined}'"
        snippet=f"Resultado sintetico {i} para a consulta '{joined}', simulando pesquisa em fontes confiaveis."
        source=f"stub://research/{mode}/{i}"
        results.append(ResearchResult(rank=i,title=title,snippet=snippet,source=source,score=score))
    return results
@router.post("/search", response_model=ResearchResponse)
def research_search(request: ResearchQuery) -> ResearchResponse:
    results=_make_stub_results(request.query,request.max_results,request.mode)
    return ResearchResponse(query=request.query,mode=request.mode,results=results,meta={"version":"step452-v1","created_at":datetime.utcnow().isoformat()+"Z","engine":"research_agent_step452_stub"})
