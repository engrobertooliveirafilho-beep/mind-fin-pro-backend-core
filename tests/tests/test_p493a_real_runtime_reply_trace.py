import inspect
from pathlib import Path

def test_p493a_trace_hook_present():
    txt = Path("app/api/whatsapp.py").read_text(encoding="utf-8", errors="ignore")
    assert "P4.93A_REAL_RUNTIME_REPLY_TRACE" in txt
    assert "_p493a_real_runtime_reply_trace" in txt
    assert "ENTER_eldora_primary_runtime_reply" in txt

def test_p493a_primary_reply_exists():
    import app.api.whatsapp as w
    assert hasattr(w, "eldora_primary_runtime_reply")
    assert callable(w.eldora_primary_runtime_reply)

def test_p493a_no_mind_os_behavior_switch_yet():
    txt = Path("app/api/whatsapp.py").read_text(encoding="utf-8", errors="ignore")
    assert "contract_dependency_resolver" not in txt
    assert "dependency_inference_engine" not in txt
    assert "resolve_contract_dependencies" not in txt
