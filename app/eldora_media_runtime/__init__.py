"""Runtime executável de mídia da Eldora.

Este pacote preserva o cânone visual existente e opera em modo fail-closed.
"""
from .pipeline import EldoraMediaPipeline

__all__ = ["EldoraMediaPipeline"]