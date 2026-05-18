import os
from app.api.whatsapp import eldora_primary_runtime_reply

def test_whatsapp_pipeline_receives_activation_context():
    os.environ["ELDORA_WHATSAPP_INTELLIGENCE_ACTIVE"]="1"
    out=eldora_primary_runtime_reply("whatsapp:+55","prosseguir ativação Eldora")
    assert isinstance(out,str)
    assert len(out) > 10
    os.environ.pop("ELDORA_WHATSAPP_INTELLIGENCE_ACTIVE",None)
