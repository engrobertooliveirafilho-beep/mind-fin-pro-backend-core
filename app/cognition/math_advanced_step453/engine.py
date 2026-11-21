from datetime import datetime, timezone
from typing import List, Dict, Any, Literal, Optional
from math import isfinite

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

MathMode = Literal["finance", "algebra", "proof"]


class FinancePayload(BaseModel):
    rate: float = Field(..., gt=-1.0)
    cashflows: List[float] = Field(..., max_length=4096)


class AlgebraPayload(BaseModel):
    a: float
    b: float


class ProofPayload(BaseModel):
    statement: str = Field(..., min_length=1, max_length=4096)
    assumptions: List[str] = Field(default_factory=list, max_length=128)


class MathRequest(BaseModel):
    mode: MathMode
    finance: Optional[FinancePayload] = None
    algebra: Optional[AlgebraPayload] = None
    proof: Optional[ProofPayload] = None


class MathResponse(BaseModel):
    mode: MathMode
    result: Dict[str, Any]
    explanation: str
    meta: Dict[str, Any]


def _npv(rate: float, cashflows: List[float]) -> float:
    if not cashflows:
        return 0.0
    r = rate
    total = 0.0
    for t, cf in enumerate(cashflows, start=0):
        denom = (1.0 + r) ** t if r != -1.0 else 1.0
        total += cf / denom
    return total


def _solve_linear(a: float, b: float) -> Dict[str, Any]:
    if a == 0:
        if b == 0:
            return {"type": "infinite_solutions"}
        return {"type": "no_solution"}
    x = -b / a
    return {"type": "unique_solution", "x": x}


def _build_proof_outline(statement: str, assumptions: List[str]) -> Dict[str, Any]:
    return {
        "steps": [
            {"step": 1, "kind": "assumptions", "content": assumptions},
            {"step": 2, "kind": "goal", "content": statement},
            {"step": 3, "kind": "strategy", "content": "dividir em casos, analisar riscos, concluir por implicacao."},
        ]
    }


@router.post("/solve", response_model=MathResponse)
def solve_math(request: MathRequest) -> MathResponse:
    if request.mode == "finance":
        if not request.finance:
            raise HTTPException(status_code=422, detail='finance payload required')
        if not isfinite(request.finance.rate) or any(not isfinite(cf) for cf in request.finance.cashflows):
            raise HTTPException(status_code=422, detail='nonfinite finance input')
        try:
            npv_value = _npv(request.finance.rate, request.finance.cashflows)
        except (OverflowError, ZeroDivisionError):
            raise HTTPException(status_code=422, detail='finance arithmetic overflow')
        if not isfinite(npv_value):
            raise HTTPException(status_code=422, detail='nonfinite NPV')
        result = {
            "npv": round(npv_value, 4),
            "rate": request.finance.rate,
            "cashflows_count": len(request.finance.cashflows),
        }
        explanation = "NPV calculado como soma dos fluxos trazidos a valor presente."

    elif request.mode == "algebra":
        if not request.algebra:
            raise HTTPException(status_code=422, detail='algebra payload required')
        if not all(isfinite(v) for v in (request.algebra.a, request.algebra.b)):
            raise HTTPException(status_code=422, detail='nonfinite algebra input')
        sol = _solve_linear(request.algebra.a, request.algebra.b)
        if 'x' in sol and not isfinite(sol['x']):
            raise HTTPException(status_code=422, detail='nonfinite algebra solution')
        result = {"equation": f"{request.algebra.a} * x + {request.algebra.b} = 0", **sol}
        explanation = "Resolvida equacao linear simples ax + b = 0."

    else:  # proof
        if not request.proof:
            raise HTTPException(status_code=422, detail='proof payload required')
        outline = _build_proof_outline(request.proof.statement, request.proof.assumptions)
        result = {"outline": outline}
        explanation = "Gerado esqueleto de prova estruturada (nao formal)."

    return MathResponse(
        mode=request.mode,
        result=result,
        explanation=explanation,
        meta={
            "version": "step453-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            "engine": "math_advanced_step453",
        },
    )

