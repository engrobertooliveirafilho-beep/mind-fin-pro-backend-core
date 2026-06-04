
from pathlib import Path

def test_runtime_has_numeric_repair_retry():
    s=Path("app/runtime/semantic_whatsapp_runtime.py").read_text(encoding="utf-8")
    assert "Não vou chutar número" in s
    assert "repair_msg" in s
    assert "sem inventar números" in s
