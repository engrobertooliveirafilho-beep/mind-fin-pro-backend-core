from __future__ import annotations

import re
import unicodedata
from typing import Any


RULE_FAMILIES = (
    "response_length",
    "format",
    "example",
    "technical_level",
    "confirmation",
    "formality",
)

SAFETY_PRECEDENCE = 1000
EXPLICIT_CORRECTION_PRECEDENCE = 800
CURRENT_EXPLICIT_REQUEST_PRECEDENCE = 700
PERSISTED_PREFERENCE_PRECEDENCE = 500
RELATIONSHIP_PRECEDENCE = 300


def _normalize(value: Any) -> str:
    text = str(value or "").strip().lower()

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _candidate(
    family: str,
    value: str,
    source: str,
    precedence: int,
    confidence: float = 0.5,
    weight: float = 0.5,
    instruction: str = "",
) -> dict[str, Any]:
    return {
        "family": family,
        "value": value,
        "source": source,
        "precedence": int(precedence),
        "confidence": float(confidence),
        "weight": float(weight),
        "instruction": str(
            instruction or ""
        ).strip(),
    }


def detect_instruction_rules(
    instruction: str,
    source: str,
    precedence: int,
) -> list[dict[str, Any]]:
    raw = str(instruction or "").strip()
    text = _normalize(raw)

    if not text:
        return []

    rules: list[dict[str, Any]] = []

    if any(
        token in text
        for token in (
            "responda curto",
            "resposta curta",
            "no maximo duas frases",
            "duas frases",
            "seja breve",
            "resuma",
        )
    ):
        rules.append(
            _candidate(
                "response_length",
                "short",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "explique detalhado",
            "explique em detalhes",
            "resposta detalhada",
            "aprofunde",
            "com profundidade",
        )
    ):
        rules.append(
            _candidate(
                "response_length",
                "detailed",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "nao use lista",
            "sem lista",
            "texto corrido",
        )
    ):
        rules.append(
            _candidate(
                "format",
                "avoid_list",
                source,
                precedence,
                instruction=raw,
            )
        )

    elif any(
        token in text
        for token in (
            "use lista",
            "em lista",
            "passo a passo",
            "em topicos",
        )
    ):
        rules.append(
            _candidate(
                "format",
                "prefer_list",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "nao use exemplo",
            "sem exemplo",
            "nao de exemplo",
        )
    ):
        rules.append(
            _candidate(
                "example",
                "avoid",
                source,
                precedence,
                instruction=raw,
            )
        )

    elif any(
        token in text
        for token in (
            "de um exemplo",
            "use exemplo",
            "inclua exemplo",
            "sempre de um exemplo",
        )
    ):
        rules.append(
            _candidate(
                "example",
                "prefer",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "linguagem tecnica",
            "mais tecnico",
            "mais tecnica",
            "nivel avancado",
        )
    ):
        rules.append(
            _candidate(
                "technical_level",
                "advanced",
                source,
                precedence,
                instruction=raw,
            )
        )

    elif any(
        token in text
        for token in (
            "linguagem simples",
            "mais simples",
            "para iniciante",
            "sem jargao",
        )
    ):
        rules.append(
            _candidate(
                "technical_level",
                "simple",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "nao execute sem confirmar",
            "confirme antes",
            "pergunte antes",
            "antes de executar",
        )
    ):
        rules.append(
            _candidate(
                "confirmation",
                "require",
                source,
                precedence,
                instruction=raw,
            )
        )

    if (
        any(
            token in text
            for token in (
                "nao precisa confirmar",
                "sem confirmacao",
                "execute direto",
            )
        )
        and
        "nao execute sem confirmar"
        not in text
    ):
        rules.append(
            _candidate(
                "confirmation",
                "avoid",
                source,
                precedence,
                instruction=raw,
            )
        )

    if any(
        token in text
        for token in (
            "tom informal",
            "sem formalidade",
            "fala normal",
        )
    ):
        rules.append(
            _candidate(
                "formality",
                "informal",
                source,
                precedence,
                instruction=raw,
            )
        )

    elif any(
        token in text
        for token in (
            "tom formal",
            "seja formal",
            "linguagem profissional",
        )
    ):
        rules.append(
            _candidate(
                "formality",
                "formal",
                source,
                precedence,
                instruction=raw,
            )
        )

    return rules


def preference_candidates(
    preferences: dict[str, Any] | None,
    effectiveness: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(preferences, dict):
        return []

    effectiveness = (
        effectiveness
        if isinstance(effectiveness, dict)
        else {}
    )

    mapping = {
        "response_length": {
            "short": "short",
            "detailed": "detailed",
        },
        "list_preference": {
            "avoid": "avoid_list",
            "prefer": "prefer_list",
        },
        "example_preference": {
            "avoid": "avoid",
            "prefer": "prefer",
        },
        "technical_level": {
            "simple": "simple",
            "advanced": "advanced",
        },
        "confirmation_preference": {
            "require": "require",
            "avoid": "avoid",
        },
        "formality": {
            "informal": "informal",
            "formal": "formal",
        },
    }

    family_alias = {
        "list_preference": "format",
        "example_preference": "example",
        "confirmation_preference": "confirmation",
    }

    result: list[dict[str, Any]] = []

    for key, values in mapping.items():
        raw_value = preferences.get(key)

        if raw_value not in values:
            continue

        family = family_alias.get(
            key,
            key,
        )

        metric = effectiveness.get(
            family,
            {},
        )

        result.append(
            _candidate(
                family,
                values[raw_value],
                "persisted_preference",
                PERSISTED_PREFERENCE_PRECEDENCE,
                confidence=float(
                    metric.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                ),
                weight=float(
                    metric.get(
                        "weight",
                        0.5,
                    )
                    or 0.5
                ),
                instruction=(
                    f"{key}={raw_value}"
                ),
            )
        )

    return result


def correction_candidates(
    corrections: list[dict[str, Any]] | None,
    effectiveness: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(corrections, list):
        return []

    effectiveness = (
        effectiveness
        if isinstance(effectiveness, dict)
        else {}
    )

    result: list[dict[str, Any]] = []

    for correction in corrections:
        if not isinstance(correction, dict):
            continue

        if correction.get("active") is not True:
            continue

        instruction = str(
            correction.get(
                "instruction",
                "",
            )
            or ""
        ).strip()

        correction_type = str(
            correction.get(
                "type",
                "",
            )
            or ""
        ).strip()

        metric = effectiveness.get(
            correction_type,
            {},
        )

        reinforcement = int(
            correction.get(
                "times_reinforced",
                1,
            )
            or 1
        )

        for candidate in detect_instruction_rules(
            instruction,
            source="explicit_correction",
            precedence=EXPLICIT_CORRECTION_PRECEDENCE,
        ):
            candidate["confidence"] = float(
                metric.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            )

            candidate["weight"] = float(
                metric.get(
                    "weight",
                    0.5,
                )
                or 0.5
            )

            candidate["reinforcement"] = (
                reinforcement
            )

            result.append(candidate)

    return result


def safety_candidates(
    action_is_destructive: bool,
) -> list[dict[str, Any]]:
    if not action_is_destructive:
        return []

    return [
        _candidate(
            "confirmation",
            "require",
            "safety_policy",
            SAFETY_PRECEDENCE,
            confidence=1.0,
            weight=1.0,
            instruction=(
                "Ações destrutivas exigem confirmação."
            ),
        )
    ]


def _candidate_score(
    candidate: dict[str, Any],
) -> tuple[float, float, float, float]:
    return (
        float(
            candidate.get(
                "precedence",
                0,
            )
            or 0
        ),
        float(
            candidate.get(
                "confidence",
                0.0,
            )
            or 0.0
        ),
        float(
            candidate.get(
                "weight",
                0.5,
            )
            or 0.5
        ),
        float(
            candidate.get(
                "reinforcement",
                1,
            )
            or 1
        ),
    )


def resolve_rule_conflicts(
    current_message: str = "",
    preferences: dict[str, Any] | None = None,
    corrections: list[dict[str, Any]] | None = None,
    effectiveness: dict[str, Any] | None = None,
    relationship: dict[str, Any] | None = None,
    action_is_destructive: bool = False,
) -> dict[str, Any]:
    effectiveness = (
        effectiveness
        if isinstance(effectiveness, dict)
        else {}
    )

    candidates: list[dict[str, Any]] = []

    candidates.extend(
        safety_candidates(
            action_is_destructive
        )
    )

    candidates.extend(
        detect_instruction_rules(
            current_message,
            source="current_explicit_request",
            precedence=(
                CURRENT_EXPLICIT_REQUEST_PRECEDENCE
            ),
        )
    )

    candidates.extend(
        correction_candidates(
            corrections,
            effectiveness,
        )
    )

    candidates.extend(
        preference_candidates(
            preferences,
            effectiveness,
        )
    )

    if isinstance(relationship, dict):
        preferred_tone = relationship.get(
            "preferred_tone"
        )

        if preferred_tone in (
            "formal",
            "informal",
        ):
            candidates.append(
                _candidate(
                    "formality",
                    preferred_tone,
                    "relationship_state",
                    RELATIONSHIP_PRECEDENCE,
                    instruction=(
                        f"preferred_tone="
                        f"{preferred_tone}"
                    ),
                )
            )

    resolved: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []

    for family in RULE_FAMILIES:
        family_candidates = [
            candidate
            for candidate in candidates
            if candidate.get("family") == family
        ]

        if not family_candidates:
            continue

        family_candidates.sort(
            key=_candidate_score,
            reverse=True,
        )

        winner = family_candidates[0]

        distinct_values = {
            candidate.get("value")
            for candidate in family_candidates
        }

        resolved[family] = winner

        if len(distinct_values) > 1:
            conflicts.append({
                "family": family,
                "winner": winner,
                "losers": family_candidates[1:],
                "resolution_basis": (
                    "precedence_then_confidence_"
                    "then_weight_then_reinforcement"
                ),
            })

    return {
        "resolved_rules": resolved,
        "conflicts": conflicts,
        "candidate_count": len(candidates),
        "conflict_count": len(conflicts),
        "action_is_destructive": bool(
            action_is_destructive
        ),
    }


def conflict_resolution_prompt_context(
    resolution: dict[str, Any],
) -> dict[str, Any]:
    resolved = resolution.get(
        "resolved_rules",
        {},
    )

    if not isinstance(resolved, dict):
        resolved = {}

    compact = {}

    for family, candidate in resolved.items():
        if not isinstance(candidate, dict):
            continue

        compact[family] = {
            "value": candidate.get("value"),
            "source": candidate.get("source"),
            "precedence": candidate.get(
                "precedence"
            ),
            "confidence": candidate.get(
                "confidence"
            ),
            "weight": candidate.get("weight"),
        }

    return {
        "resolved_conversation_rules": compact,
        "resolved_conflict_count": int(
            resolution.get(
                "conflict_count",
                0,
            )
            or 0
        ),
    }
