
from app.runtime.generic_conversation_state import update_conversation_state, progressive_answer
from app.runtime.global_topic_authority import global_topic_authority

def test_generic_eldora_deepen_does_not_bleed_vehicle():
    global_topic_authority("Primeiro: melhorar fluidez","Sobre Eldora, quero melhorar fluidez","u1")
    out=global_topic_authority("Ação: buscar kick starter CR250R","aprofunde","u1")
    assert "CR250R" not in out
    assert "Eldora" in out or "fluidez" in out or "autoridade" in out

def test_generic_vehicle_deepen_does_not_bleed_eldora():
    global_topic_authority("Preço IMS encontrado","CR250R 2001 pedal de partida","u2")
    out=global_topic_authority("Sobre Eldora runtime","aprofunde","u2")
    assert "Eldora" not in out
    assert len(out)>20

def test_state_tracks_topic_entities_intent_stage():
    st=update_conversation_state("u3","Sobre Eldora, quero melhorar fluidez")
    assert st.active_topic=="eldora_runtime_ux"
    st2=update_conversation_state("u3","aprofunde")
    assert st2.intent=="deepen"
    order=["summary","detail","compare","decision","action","validation"]
    assert order.index(st2.stage)>order.index(st.stage)
