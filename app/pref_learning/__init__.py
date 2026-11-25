"""
STEP 541 - Long-Horizon Preference Learning

Aprendizado de preferencias de longo prazo:
- agrega sinais ao longo do tempo por user_id
- calcula médias simples, sem tocar em dados reais
"""

from .engine import LongHorizonPreferenceLearner

__all__ = ["LongHorizonPreferenceLearner"]

