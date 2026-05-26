
import pytest
from app.runtime.universal_conversation_os import UniversalConversationOS, universal_conversation_guard, FORBIDDEN

CASES=[
("smalltalk","fala Roberto, bom dia","SOCIAL"),
("smalltalk_typo","como vc tá?","SOCIAL"),
("calc","calcula 20 + 30","CALCULATION"),
("calc_syn","quanto dá 7*8","CALCULATION"),
("analysis","analisa esse documento","ANALYSIS"),
("verify","verifica esse problema","VERIFICATION"),
("execution","busque pelo problema","EXECUTION"),
("strategy","monte uma estratégia de lançamento","TASK"),
]
@pytest.mark.parametrize("name,msg,expected",CASES)
def test_mode_classes(name,msg,expected):
    r=UniversalConversationOS.process(msg,f"sender_{name}")
    assert r["mode"]==expected
    assert r["reply"]
    assert not any(b.lower() in r["reply"].lower() for b in FORBIDDEN)

def test_followup_continuity():
    s="sender_follow"
    UniversalConversationOS.process("preciso corrigir o webhook do whatsapp",s)
    r=UniversalConversationOS.process("aprofundar",s)
    assert r["mode"]=="FOLLOWUP"
    assert "webhook" in r["topic"].lower() or "whatsapp" in r["topic"].lower()

def test_final_guard_blocks_placeholder_candidate():
    out=universal_conversation_guard("oi","sender_guard","Resposta direta: teste. Ação recomendada: teste.")
    assert "Resposta direta:" not in out
    assert "Ação recomendada:" not in out
