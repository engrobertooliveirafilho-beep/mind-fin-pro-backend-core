from app.dialogue.context_resolution_engine import resolve
from app.dialogue.conversation_continuity_runtime import update
def test_context_resolution():
    update("r","qual o proximo passo agora?")
    update("r","implantações da eldora")
    out=resolve("r","isso")
    assert "implant" in out.lower()
