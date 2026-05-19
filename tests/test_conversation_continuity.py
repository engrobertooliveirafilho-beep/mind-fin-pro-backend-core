from app.dialogue.conversation_continuity_runtime import update,get
def test_context_continuity():
    update("r","qual o proximo passo agora?")
    s=update("r","isso, sobre as implantações")
    assert "implant" in s["active_topic"].lower()
    assert s["continuity_confidence"]>=0.9
