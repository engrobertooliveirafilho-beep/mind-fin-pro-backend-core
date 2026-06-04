
from app.runtime.subject_alias_engine import subject_alias
from app.runtime.relational_conversation_engine import relationalize

def test_subject_alias_never_returns_isso():
    assert subject_alias("quero comprar um corolla") == "corolla"
    assert subject_alias("quero comprar um helicóptero robinson r44") == "helicóptero robinson r44"
    assert subject_alias("") == ""

def test_relationalize_does_not_replace_subject_with_isso():
    ctx={"last_subject":"quero comprar um corolla"}
    out=relationalize("vale a pena?","Eu teria coragem, mas só se a quero comprar um corolla estiver inteira.",ctx)
    assert "isso" not in out.lower()
    assert "corolla" in out.lower()

