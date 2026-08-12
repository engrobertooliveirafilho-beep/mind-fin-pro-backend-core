from pathlib import Path
import re

path = Path("app/runtime/knowledge_extraction_engine.py")
text = path.read_text(encoding="utf-8", errors="ignore")

if "def _p482h_original_extract_items" not in text:
    text = re.sub(
        r"def\s+extract_items\s*\(",
        "def _p482h_original_extract_items(",
        text,
        count=1
    )

wrapper = r'''

def extract_items(source_id, text, metadata=None):
    out = _p482h_original_extract_items(source_id, text, metadata)

    if not isinstance(out, dict):
        return out

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (text or "").lower()
    existing = str(items).lower()

    def add(kind, value):
        items.append({
            "type": kind,
            "value": value,
            "source": "P4.82H_WRAPPER"
        })

    if ("memória" in low or "memoria" in low) and "capability" not in existing:
        add("CAPABILITY", "Memória persistente detectada.")

    if ("não foi implementado" in low or "nao foi implementado" in low or "ainda não foi implementado" in low) and "unimplemented" not in existing:
        add("UNIMPLEMENTED_IDEA", "Ideia não implementada detectada.")

    if "bug" in low and "bug_fix" not in existing:
        add("BUG_FIX", "Bug detectado.")

    if "arquitetura" in low and "architecture" not in existing:
        add("ARCHITECTURE", "Arquitetura detectada.")

    out["items"] = items
    out["total_items"] = max(int(out.get("total_items", 0) or 0), len(items))
    return out
'''

if "P4.82H_WRAPPER" not in text:
    text += wrapper

path.write_text(text, encoding="utf-8")
print("P4.82H wrapper applied")
