from __future__ import annotations

import importlib
from typing import Any, Dict, List

# P19P36G_SAFE_RECOVERY_ADAPTER
# Shadow-only adapter: não altera resposta, não altera fluxo vivo.
# Apenas tenta recuperar sinais de módulos existentes com segurança.

RECOVERED_MODULES = [
    # preenchido dinamicamente por auditoria futura, mantido vazio/seguro por padrão
]

def safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def collect_recovered_context(sender: str, text: str, base_ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(base_ctx or {})
    recovered: List[Dict[str, Any]] = []

    for module_name in RECOVERED_MODULES:
        mod = safe_import(module_name)
        if not mod:
            continue

        payload = {"module": module_name, "signals": {}}

        for fn_name in ["get", "resolve", "recall", "load", "get_context", "get_memory", "get_profile"]:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    payload["signals"][fn_name] = str(fn(sender))[:500]
                except TypeError:
                    try:
                        payload["signals"][fn_name] = str(fn(sender, text))[:500]
                    except Exception:
                        pass
                except Exception:
                    pass

        if payload["signals"]:
            recovered.append(payload)

    ctx["recovered_shadow_context"] = recovered
    return ctx

def enrich_reply_shadow(sender: str, text: str, base_ctx: Dict[str, Any], reply: str) -> str:
    # Shadow mode: não modifica a resposta.
    return reply
# /P19P36G_SAFE_RECOVERY_ADAPTER
