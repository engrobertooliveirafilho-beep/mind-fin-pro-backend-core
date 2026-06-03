
from app.runtime.conversation_state_machine import build_conversation_payload, detect_subject

def test_new_strong_entity_replaces_previous_subject():
    ctx={}
    build_conversation_payload("quero comprar uma RAM 2500 ano 2026", ctx)
    assert "ram 2500" in ctx["last_subject"]
    build_conversation_payload("quero comprar um Corolla", ctx)
    assert "corolla" in ctx["last_subject"]
    assert "ram" not in ctx["last_subject"]

def test_universal_subject_without_known_brand_list():
    ctx={}
    build_conversation_payload("quero comprar um helicóptero Robinson R44", ctx)
    assert "robinson r44" in ctx["last_subject"]
    out=build_conversation_payload("vale a pena?", ctx)
    assert "ASSUNTO ATUAL" in out
    assert "robinson r44" in out

def test_universal_non_vehicle_subject():
    ctx={}
    build_conversation_payload("quero montar uma fábrica de ração automatizada", ctx)
    assert "fábrica de ração" in ctx["last_subject"]
    out=build_conversation_payload("me explique", ctx)
    assert "ASSUNTO ATUAL" in out
    assert "fábrica de ração" in out

def test_no_old_vehicle_model_hardcodes_in_live_engine():
    import pathlib
    s=pathlib.Path("app/runtime/conversation_state_machine.py").read_text(encoding="utf-8").lower()
    forbidden=["cb500","fazer 250","k1300","hornet","xre 300","mt03","ram 2500","corolla","crf 450"]
    assert not any(x in s for x in forbidden)
