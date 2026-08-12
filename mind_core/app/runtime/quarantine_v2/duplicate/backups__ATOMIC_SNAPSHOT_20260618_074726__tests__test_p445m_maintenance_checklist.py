
from pathlib import Path

def test_vehicle_maintenance_checklist_prompt_exists():
    s=Path("app/runtime/generic_topic_memory_engine.py").read_text(encoding="utf-8").lower()
    assert "histórico de manutenção" in s or "historico de manutencao" in s
    assert "disponibilidade de peças" in s or "disponibilidade de pecas" in s
    assert "motor" in s
    assert "transmissão" in s or "transmissao" in s
