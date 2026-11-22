import hashlib
from typing import Dict, Any, List


class CreativeDNAEngine:
    """
    Gera e evolui o DNA criativo de uma marca de forma determinística.
    """

    _TRAITS = [
        'boldness',
        'warmth',
        'complexity',
        'playfulness',
        'minimalism',
        'contrast',
        'motion',
        'experimentation',
    ]

    def __init__(self, brand_id: str, seed: str | None = None) -> None:
        if not isinstance(brand_id, str) or not brand_id.strip():
            raise ValueError('brand_id must be a non-empty string.')
        if seed is not None and (not isinstance(seed, str) or not seed.strip()):
            raise ValueError('seed must be a non-empty string if provided.')

        self.brand_id = brand_id.strip()
        self.seed = seed.strip() if isinstance(seed, str) and seed.strip() else 'default'
        self.version = 'step210-v1'
        self._history: List[Dict[str, Any]] = []
        self._dna = self._build_base_dna()
        self._record_history('init', {'brand_id': self.brand_id, 'seed': self.seed})

    def _record_history(self, reason: str, meta: Dict[str, Any]) -> None:
        self._history.append(
            {
                'index': len(self._history),
                'reason': reason,
                'meta': dict(meta),
                'snapshot': self._dna.copy(),
            }
        )

    @staticmethod
    def _norm01(v: float) -> float:
        return max(0.0, min(1.0, float(v)))

    def _build_base_dna(self) -> Dict[str, Any]:
        base_key = f'{self.brand_id}::{self.seed}'.encode('utf-8')
        digest = hashlib.sha256(base_key).hexdigest()

        traits: Dict[str, float] = {}
        # usa 2 hex por traço
        for i, name in enumerate(self._TRAITS):
            start = (i * 2) % len(digest)
            chunk = digest[start : start + 2]
            val = int(chunk, 16) / 255.0
            traits[name] = round(val, 4)

        palette_seed = hashlib.sha256((self.brand_id + '::palette').encode('utf-8')).hexdigest()[:12]
        tone_seed = hashlib.sha256((self.brand_id + '::tone').encode('utf-8')).hexdigest()[:12]

        return {
            'brand_id': self.brand_id,
            'seed': self.seed,
            'traits': traits,
            'palette_seed': palette_seed,
            'tone_seed': tone_seed,
        }

    def get_dna(self) -> Dict[str, Any]:
        return {
            'brand_id': self._dna['brand_id'],
            'seed': self._dna['seed'],
            'traits': dict(self._dna['traits']),
            'palette_seed': self._dna['palette_seed'],
            'tone_seed': self._dna['tone_seed'],
            'version': self.version,
            'history_length': len(self._history),
        }

    def nudge(self, adjustments: Dict[str, float], reason: str = 'nudge') -> Dict[str, Any]:
        if not isinstance(adjustments, dict):
            raise ValueError('adjustments must be a dict.')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('reason must be a non-empty string.')

        traits = dict(self._dna['traits'])
        for k, delta in adjustments.items():
            if k not in traits:
                continue
            if not isinstance(delta, (int, float)):
                raise ValueError('adjustment values must be numeric.')
            traits[k] = self._norm01(traits[k] + float(delta))

        self._dna['traits'] = traits
        self._record_history(reason.strip(), {'adjustments': dict(adjustments)})
        return self.get_dna()

    def blend_with(self, other_dna: Dict[str, Any], weight: float = 0.5, reason: str = 'blend') -> Dict[str, Any]:
        if not isinstance(other_dna, dict):
            raise ValueError('other_dna must be a dict.')
        if not isinstance(weight, (int, float)):
            raise ValueError('weight must be numeric.')
        w = self._norm01(weight)

        other_traits = other_dna.get('traits')
        if not isinstance(other_traits, dict):
            raise ValueError('other_dna.traits must be a dict.')

        traits = dict(self._dna['traits'])
        for k in self._TRAITS:
            a = traits.get(k, 0.5)
            b = float(other_traits.get(k, 0.5))
            mixed = (1.0 - w) * a + w * b
            traits[k] = round(self._norm01(mixed), 4)

        self._dna['traits'] = traits
        # mistura seeds só como concat simbólico
        self._dna['palette_seed'] = (self._dna['palette_seed'] + '+' + str(other_dna.get('palette_seed', '')))[:24]
        self._dna['tone_seed'] = (self._dna['tone_seed'] + '+' + str(other_dna.get('tone_seed', '')))[:24]

        self._record_history(reason, {'weight': w})
        return self.get_dna()

    def history_summary(self) -> Dict[str, Any]:
        return {
            'brand_id': self.brand_id,
            'seed': self.seed,
            'events': len(self._history),
            'version': self.version,
        }

