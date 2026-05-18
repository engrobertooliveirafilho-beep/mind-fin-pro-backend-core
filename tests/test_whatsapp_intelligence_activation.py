import os
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active

def test_whatsapp_intelligence_activation_flag():
    os.environ["ELDORA_WHATSAPP_INTELLIGENCE_ACTIVE"]="1"
    out=enrich_whatsapp_context("whatsapp:+55","prosseguir")
    assert whatsapp_intelligence_active() is True
    assert out["status"]=="operational"
    assert out["runtime_modules_count"] > 0
    assert out["activation_mode"]=="controlled_feature_flag"
    os.environ.pop("ELDORA_WHATSAPP_INTELLIGENCE_ACTIVE",None)
