from typing import Dict, Any, List


class ComputationalWillEngine:
    """Núcleo de vontade computacional: escolhe direção entre opções."""

    def __init__(self) -> None:
        # Mesmas dimensões filosóficas da MIND (coerente com Purpose Kernel)
        self._default_weights: Dict[str, float] = {
            "user_benefit": 0.35,
            "safety": 0.25,
            "long_term": 0.2,
            "cashflow": 0.1,
            "learning": 0.1,
        }
        self._last_decision: Dict[str, Any] = {}

    @property
    def last_decision(self) -> Dict[str, Any]:
        return self._last_decision

    def _clamp(self, value: float, default: float = 0.5) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = default
        return max(0.0, min(1.0, v))

    def _normalize_weights(self, raw_weights: Dict[str, Any]) -> Dict[str, float]:
        weights: Dict[str, float] = {}
        for key, default in self._default_weights.items():
            raw_value = raw_weights.get(key, default)
            weights[key] = self._clamp(raw_value, default=default)
        return weights

    def decide(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        options_raw = payload.get("options") or []
        if not isinstance(options_raw, list) or not options_raw:
            result = {
                "error": "no_options",
                "options": [],
                "winner": None,
                "weights": dict(self._default_weights),
            }
            self._last_decision = result
            return result

        raw_weights = payload.get("weights") or {}
        if not isinstance(raw_weights, dict):
            raw_weights = {}
        weights = self._normalize_weights(raw_weights)
        total_weight = sum(weights.values()) or 1.0

        scored_options: List[Dict[str, Any]] = []
        for idx, opt in enumerate(options_raw):
            if not isinstance(opt, dict):
                continue

            opt_id = opt.get("id") or opt.get("name") or f"opt_{idx}"
            opt_id = str(opt_id)
            scores_raw = opt.get("scores") or {}
            if not isinstance(scores_raw, dict):
                scores_raw = {}

            normalized_scores: Dict[str, float] = {}
            for dim in self._default_weights.keys():
                normalized_scores[dim] = self._clamp(scores_raw.get(dim, 0.5))

            raw_score = 0.0
            for dim, w in weights.items():
                raw_score += w * normalized_scores[dim]
            final_score = raw_score / total_weight

            scored_options.append(
                {
                    "id": opt_id,
                    "scores": normalized_scores,
                    "final_score": float(final_score),
                    "meta": opt.get("meta") or {},
                }
            )

        if not scored_options:
            result = {
                "error": "no_valid_options",
                "options": [],
                "winner": None,
                "weights": weights,
            }
            self._last_decision = result
            return result

        scored_options.sort(key=lambda o: o["final_score"], reverse=True)
        winner = scored_options[0]

        result = {
            "options": scored_options,
            "winner": winner,
            "weights": weights,
        }
        self._last_decision = result
        return result


engine = ComputationalWillEngine()

