from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LineageEdge:
    """
    STEP 524 - Aresta de linhagem de dados.
    source -> target, com metadados mínimos.
    """
    source: str
    target: str
    metadata: Dict[str, Any]


class LineageGraph:
    """
    STEP 524 - Grafo mínimo de linhagem de dados.

    100% em memória, isolado.
    Futuro: persistência, integração com módulos reais.
    """

    def __init__(self) -> None:
        self._edges: List[LineageEdge] = []

    @property
    def edges(self) -> List[LineageEdge]:
        return list(self._edges)

    def add_edge(self, source: str, target: str, metadata: Dict[str, Any] | None = None) -> LineageEdge:
        edge = LineageEdge(source=source, target=target, metadata=metadata or {})
        self._edges.append(edge)
        return edge

    def get_upstream(self, node: str) -> List[LineageEdge]:
        return [e for e in self._edges if e.target == node]

    def get_downstream(self, node: str) -> List[LineageEdge]:
        return [e for e in self._edges if e.source == node]

