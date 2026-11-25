from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PluginInfo:
    """
    STEP 528 - Informacoes basicas de um plugin.
    """
    name: str
    scopes: List[str]
    enabled: bool = True
    meta: Dict[str, Any] | None = None


class PluginRegistry:
    """
    STEP 528 - Registro minimo de plugins.

    - registro
    - listagem
    - revogacao (desabilitar)
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginInfo] = {}

    def register_plugin(self, name: str, scopes: List[str], meta: Dict[str, Any] | None = None) -> PluginInfo:
        info = PluginInfo(name=name, scopes=list(scopes), enabled=True, meta=meta or {})
        self._plugins[name] = info
        return info

    def revoke_plugin(self, name: str) -> None:
        if name in self._plugins:
            self._plugins[name].enabled = False

    def list_plugins(self, only_enabled: bool | None = None) -> List[PluginInfo]:
        values = list(self._plugins.values())
        if only_enabled is None:
            return values
        return [p for p in values if p.enabled == only_enabled]

