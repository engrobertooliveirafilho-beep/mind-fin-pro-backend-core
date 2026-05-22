
from app.runtime.generic_conversation_state import update_conversation_state, progressive_answer

def test_deepen_aliases_are_normalized():
    for phrase in ["aprofunde ainda mais","detalhe melhor","explique melhor","continue detalhando"]:
        st=update_conversation_state("alias_"+phrase,"Sobre Eldora quero melhorar fluidez")
        st=update_conversation_state("alias_"+phrase,phrase)
        assert st.intent=="deepen"

def test_progression_does_not_freeze_on_action():
    uid="progression_user"
    update_conversation_state(uid,"Sobre Eldora quero melhorar fluidez")
    outs=[]
    for _ in range(9):
        st=update_conversation_state(uid,"aprofunde")
        outs.append(progressive_answer("mesma resposta",st))
    assert len(set(outs)) >= 4

def test_eldora_never_bleeds_vehicle_terms():
    uid="eldora_no_bleed"
    update_conversation_state(uid,"Sobre Eldora quero melhorar fluidez")
    st=update_conversation_state(uid,"aprofunde")
    out=progressive_answer("Ação: buscar Honda CR250R kick starter",st)
    assert "CR250R" not in out
    assert "kick starter" not in out

def test_vehicle_never_bleeds_eldora_terms():
    uid="vehicle_no_bleed"
    update_conversation_state(uid,"CR250R 2001 pedal de partida")
    st=update_conversation_state(uid,"aprofunde")
    out=progressive_answer("Sobre Eldora runtime",st)
    assert "Eldora" not in out
