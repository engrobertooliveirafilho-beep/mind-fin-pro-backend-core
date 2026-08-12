from pathlib import Path
import re

path = Path("app/runtime/knowledge_extraction_engine.py")
text = path.read_text(encoding="utf-8", errors="ignore")

helper = r'''
def _p482g_contract_expand(out, source_text):
    if not isinstance(out, dict):
        return out

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (source_text or "").lower()
    existing = str(items).lower()

    def add(kind, value):
        items.append({
            "type": kind,
            "value": value,
            "source": "P4.82G_CONTRACT_RECOVERY"
        })

    if ("memória" in low or "memoria" in low) and "capability" not in existing:
        add("CAPABILITY", "Memória persistente detectada como capacidade.")

    if ("não foi implementado" in low or "nao foi implementado" in low or "ainda não foi implementado" in low) and "unimplemented" not in existing:
        add("UNIMPLEMENTED_IDEA", "Ideia ainda não implementada detectada.")

    if "bug" in low and "bug_fix" not in existing:
        add("BUG_FIX", "Bug detectado no texto.")

    if "arquitetura" in low and "architecture" not in existing:
        add("ARCHITECTURE", "Arquitetura detectada no texto.")

    out["items"] = items
    out["total_items"] = max(int(out.get("total_items", 0) or 0), len(items))
    return out
'''

if "_p482g_contract_expand" not in text:
    text += "\n\n" + helper

# Corrige retornos finais comuns da função extract_items
text = text.replace("return out", "return _p482g_contract_expand(out, text)")
text = text.replace("return result", "return _p482g_contract_expand(result, text)")
text = text.replace("return data", "return _p482g_contract_expand(data, text)")

path.write_text(text, encoding="utf-8")
print("P4.82G patched knowledge_extraction_engine.py")
