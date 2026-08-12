from app.api.whatsapp import eldora_primary_runtime_reply
from app.main import (
    _p19p26a_h8_filter_xml_response,
    _p412n_normalize_xml_response,
    primary_twiml
)

sender = "whatsapp:+5519996166906"
cases = [
    "quero emagrecer",
    "monte um plano pra mim",
    "quais",
    "crie um",
    "1kg",
    "prossiga"
]

for c in cases:
    print("CASE:", c)
    try:
        raw = eldora_primary_runtime_reply(sender, c)
    except Exception as e:
        raw = "ERR:" + repr(e)
    print("RAW:", raw)

    xml = primary_twiml(raw)
    norm = _p412n_normalize_xml_response(c, xml)
    filt = _p19p26a_h8_filter_xml_response(c, norm)

    print("FILTERED:", filt)
    print("---")
