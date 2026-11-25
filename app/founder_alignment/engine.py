from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FounderAlignmentResult:
    """
    STEP 538 - Resultado de alinhamento com o fundador.
    """
    alignment_score: float
    is_aligned: bool
    flags: List[str]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alignment_score": float(self.alignment_score),
            "is_aligned": bool(self.is_aligned),
            "flags": list(self.flags),
            "summary": self.summary,
        }


class FounderAlignmentEngine:
    """
    STEP 538 - Núcleo mínimo de alinhamento com o fundador.

    founder_profile (dict esperado):
      - vision_keywords: List[str]
      - red_lines: List[str]  (coisas que NUNCA devem aparecer)
    """

    def assess(self, plan: Dict[str, Any], founder_profile: Dict[str, Any]) -> FounderAlignmentResult:
        description = (plan.get("description") or "").lower()
        tags = [str(t).lower() for t in plan.get("tags", [])]

        vision_keywords = [v.lower() for v in founder_profile.get("vision_keywords", [])]
        red_lines = [r.lower() for r in founder_profile.get("red_lines", [])]

        flags: List[str] = []

        # checa red lines
        violates_red_line = False
        for rl in red_lines:
            if not rl:
                continue
            if rl in description or any(rl in t for t in tags):
                violates_red_line = True
                flags.append(f"violates_red_line:{rl}")

        # checa alinhamento positivo com visão
        vision_hits = 0
        for vk in vision_keywords:
            if not vk:
                continue
            if vk in description or any(vk in t for t in tags):
                vision_hits += 1

        # heurística simples de score
        if violates_red_line:
            score = 0.1
        else:
            base = 0.4
            score = min(1.0, base + 0.15 * vision_hits)

        is_aligned = (not violates_red_line) and score >= 0.6

        if violates_red_line:
            summary = "Plano viola pelo menos uma red line do fundador."
        elif is_aligned:
            summary = "Plano alinhado com a visão do fundador."
        else:
            summary = "Plano parcialmente alinhado, porém abaixo do limiar desejado."

        return FounderAlignmentResult(
            alignment_score=score,
            is_aligned=is_aligned,
            flags=flags,
            summary=summary,
        )

