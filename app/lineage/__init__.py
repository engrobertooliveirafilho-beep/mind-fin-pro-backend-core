"""
STEP 524 - Data Lineage Graph

Grafo mínimo de linhagem de dados, isolado.
Rastreia de onde veio cada dado e para onde foi.
"""

from .graph import LineageGraph, LineageEdge

__all__ = ["LineageGraph", "LineageEdge"]

