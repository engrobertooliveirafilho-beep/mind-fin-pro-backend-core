
from app.runtime.factual_session_state import infer_factual_state, should_factual_search, build_factual_prompt

def test_initial_cr250r_context():
    st=infer_factual_state("ELA É 2001 MODELO CR250R 2 TEMPOS preciso do pedal de partida quero que vc verifique")
    assert st.active_subject == "Honda CR250R 2001 2T"
    assert st.active_item == "pedal de partida"
    assert st.last_intent == "compatibility_search"
    assert should_factual_search(st)

def test_price_followup_reuses_context():
    prev=infer_factual_state("CR250R 2001 2 tempos pedal de partida IMS Red Dragon verifique")
    st=infer_factual_state("e qual o valor da IMS e Red Dragon?", prev)
    assert st.active_item == "pedal de partida"
    assert st.active_subject == "Honda CR250R 2001 2T"
    assert st.last_intent == "price_search"
    assert "carburador" not in build_factual_prompt(st,"").lower()

def test_import_followup_reuses_context():
    prev=infer_factual_state("CR250R 2001 pedal de partida verifique")
    st=infer_factual_state("talvez importando", prev)
    assert st.last_intent == "import_search"
    assert should_factual_search(st)

def test_adaptation_followup_reuses_context():
    prev=infer_factual_state("CR250R 2001 pedal de partida verifique")
    st=infer_factual_state("consigo adaptar de outra moto?", prev)
    assert st.last_intent == "adaptation_search"
    assert should_factual_search(st)
