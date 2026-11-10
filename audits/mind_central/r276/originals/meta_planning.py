from typing import List, Literal
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ModuleProfile(BaseModel):
    module_name: str
    impact: float      # 0-1: impacto estratégico
    cost: float        # 0-1: custo de evolução
    risk: float        # 0-1: risco de mudança
    maturity: float    # 0-1: quão consolidado está


class ModulePlanEntry(BaseModel):
    module_name: str
    priority_score: float
    action: str
    reason_short: str


class MetaPlanRequest(BaseModel):
    focus: Literal["growth", "stability", "efficiency"] = "growth"
    modules: List[ModuleProfile]


class MetaPlanResponse(BaseModel):
    focus: str
    plan: List[ModulePlanEntry]


def _clamp(x: float, min_v: float = 0.0, max_v: float = 1.0) -> float:
    return max(min_v, min(max_v, x))


def suggest_evolution_plan(focus: str, modules: List[ModuleProfile]) -> MetaPlanResponse:
    entries: List[ModulePlanEntry] = []

    for m in modules:
        impact = _clamp(m.impact)
        cost = _clamp(m.cost)
        risk = _clamp(m.risk)
        maturity = _clamp(m.maturity)

        # score base: alto impacto + boa maturidade, penaliza custo e risco
        base_score = impact * 0.5 + maturity * 0.3 - cost * 0.1 - risk * 0.1

        # ajustes por foco global
        if focus == "growth":
            score = base_score + impact * 0.2
        elif focus == "stability":
            score = base_score + (1.0 - risk) * 0.2 + maturity * 0.1
        else:  # efficiency
            score = base_score + (1.0 - cost) * 0.2

        score = round(score, 4)

        if score >= 0.7:
            action = "accelerate"
            reason = "alto impacto e boa relação risco/custo"
        elif score >= 0.4:
            action = "maintain"
            reason = "relevante, mas não crítico; manter evolução gradual"
        else:
            action = "monitor"
            reason = "baixo retorno relativo; apenas acompanhar"

        entries.append(
            ModulePlanEntry(
                module_name=m.module_name,
                priority_score=score,
                action=action,
                reason_short=reason,
            )
        )

    # ordenar por prioridade descendente
    entries.sort(key=lambda e: e.priority_score, reverse=True)

    return MetaPlanResponse(focus=focus, plan=entries)


@router.post("/plan", response_model=MetaPlanResponse)
def meta_plan(req: MetaPlanRequest) -> MetaPlanResponse:
    return suggest_evolution_plan(req.focus, req.modules)

