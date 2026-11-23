import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"app/runtime/p2397_offline_research_guard.py"
s=importlib.util.spec_from_file_location("p2397_guard",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def test_original_hypothesis_is_research_only():
    h={"type":"DD_REDUCTION","paper_only":True}
    e={"decision":"OBSERVE_SCORE","runtime_promotion":False}
    assert m.validate_research_hypothesis(h,e)==(False,"OFFLINE_RESEARCH_ONLY_NO_RUNTIME_AUTHORITY")

def test_promoted_runtime_rejected():
    assert m.validate_research_hypothesis({"type":"DD_REDUCTION","paper_only":True},{"decision":"OBSERVE_SCORE","runtime_promotion":True})==(False,"RUNTIME_PROMOTION_FORBIDDEN")

def test_unknown_hypothesis_rejected():
    assert m.validate_research_hypothesis({"type":"UNTRUSTED","paper_only":True},{"decision":"OBSERVE_SCORE","runtime_promotion":False})==(False,"UNKNOWN_RESEARCH_TYPE")
