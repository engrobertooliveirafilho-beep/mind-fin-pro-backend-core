
from pathlib import Path

def test_live_runtime_uses_single_subject_engine():
    s=Path("app/runtime/semantic_whatsapp_runtime.py").read_text(encoding="utf-8")
    assert "build_conversation_payload" in s
    assert "update_topic_context" not in s
    assert "update_subject_state" not in s
