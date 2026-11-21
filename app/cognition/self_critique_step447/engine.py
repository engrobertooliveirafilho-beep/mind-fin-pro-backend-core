from datetime import datetime
from typing import List, Dict, Any, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

Severity = Literal["low", "medium", "high"]


class SelfCritiqueRequest(BaseModel):
    output: str
    context: Optional[str] = None
    severity: Severity = "medium"


class CritiqueItem(BaseModel):
    code: str
    message: str
    severity: Severity


class SelfCritiqueResponse(BaseModel):
    original_output: str
    critique: List[CritiqueItem]
    corrected_output: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    meta: Dict[str, Any]


def _basic_checks(output: str, context: Optional[str], severity: Severity) -> List[CritiqueItem]:
    text = output.strip()
    issues: List[CritiqueItem] = []

    def add(code: str, msg: str, sev: Severity):
        issues.append(CritiqueItem(code=code, message=msg, severity=sev))

    if len(text) < 40:
        add("too_short", "Resposta muito curta, deveria detalhar mais implicacoes praticas.", max(severity, "medium"))  # type: ignore[arg-type]

    if "risco" not in text.lower() and (context or "").lower().find("finan") != -1:
        add("no_risk", "Resposta nao considera riscos financeiros explicitamente.", severity)

    if text.endswith("?"):
        add("uncertain", "Resposta termina em pergunta; sugere falta de conclusao firme.", "low")

    if not issues:
        add("ok", "Nenhuma falha critica identificada; apenas pequenos ajustes de clareza.", "low")

    return issues


def _severity_weight(sev: Severity) -> float:
    if sev == "low":
        return 0.9
    if sev == "medium":
        return 0.7
    return 0.4


def _compute_quality(issues: List[CritiqueItem]) -> float:
    # Quanto mais issues graves, menor a nota. Regra simples, mas padronizada.
    weights = [_severity_weight(i.severity) for i in issues]
    base = sum(weights) / max(1, len(weights))
    return round(base, 3)


def _apply_corrections(output: str, issues: List[CritiqueItem]) -> str:
    text = output.strip()
    notes = []

    for i in issues:
        if i.code == "too_short":
            notes.append("expandir com 2-3 pontos praticos.")
        elif i.code == "no_risk":
            notes.append("incluir paragrafo explicito sobre riscos e mitigacoes.")
        elif i.code == "uncertain":
            notes.append("fechar com conclusao clara, sem interrogacao.")
        elif i.code == "ok":
            notes.append("ajustar somente clareza e fluidez.")

    if not notes:
        return text

    corrections = " MELHORIAS: " + " ".join(notes)
    return f"{text} {corrections}"


@router.post("/run", response_model=SelfCritiqueResponse)
def run_self_critique(request: SelfCritiqueRequest) -> SelfCritiqueResponse:
    issues = _basic_checks(request.output, request.context, request.severity)
    quality = _compute_quality(issues)
    corrected = _apply_corrections(request.output, issues)

    return SelfCritiqueResponse(
        original_output=request.output,
        critique=issues,
        corrected_output=corrected,
        quality_score=quality,
        meta={
            "version": "step447-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "self_critique_step447",
        },
    )

