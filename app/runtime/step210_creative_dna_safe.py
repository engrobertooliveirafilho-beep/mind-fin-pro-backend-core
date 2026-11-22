"""Validated adapter for recovered creative STEP210; never a finance STEP certification."""
import math
from collections.abc import Mapping
from recovered.creative.step210_creative_dna_engine_original import CreativeDNAEngine

class SafeCreativeDNAEngine(CreativeDNAEngine):
    def nudge(self, adjustments, reason='nudge'):
        if not isinstance(adjustments, Mapping) or not isinstance(reason,str) or not reason.strip():
            raise ValueError('valid adjustments and reason required')
        for name, delta in adjustments.items():
            if name not in self._TRAITS:
                raise ValueError('unknown trait')
            if type(delta) not in (int,float) or not math.isfinite(delta):
                raise ValueError('finite numeric adjustment required')
        return super().nudge(dict(adjustments), reason)
    def blend_with(self, other_dna, weight=0.5, reason='blend'):
        if type(weight) not in (int,float) or not math.isfinite(weight):
            raise ValueError('finite numeric weight required')
        if not isinstance(reason,str) or not reason.strip():
            raise ValueError('reason required')
        if not isinstance(other_dna,Mapping) or not isinstance(other_dna.get('traits'),Mapping):
            raise ValueError('traits mapping required')
        for name in self._TRAITS:
            value=other_dna['traits'].get(name,0.5)
            if type(value) not in (int,float) or not math.isfinite(value):
                raise ValueError('finite trait required')
        return super().blend_with(dict(other_dna), weight, reason)
