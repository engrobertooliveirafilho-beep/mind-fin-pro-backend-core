
from app.runtime.universal_subject_continuity import update_subject_state, get_subject_state, reset_subject_state
def test_ram_not_motorcycle_followups():
    sid='ram'; reset_subject_state(sid)
    s=update_subject_state(sid,'quero comprar uma RAM 2500 ano 2026')
    assert s['domain']=='vehicle' and s['entity_class']=='pickup' and s['entity_class']!='motorcycle'
    assert update_subject_state(sid,'quanto ela faz por litro?')['subject']==s['subject']
    assert update_subject_state(sid,'vale a pena?')['subject']==s['subject']
    assert update_subject_state(sid,'e a manutenção?')['subject']==s['subject']
def test_general_domains():
    cases=[('quero comprar uma CRF 450','motorcycle'),('quero comprar um Corolla','car'),('quero comprar um Cane Corso','dog'),('me explique confinamento de gado','livestock'),('verifique esse contrato','document'),('problema no Render webhook','system')]
    for i,(m,cls) in enumerate(cases):
        sid=str(i); reset_subject_state(sid)
        assert update_subject_state(sid,m)['entity_class']==cls
def test_social_does_not_delete_subject():
    sid='social'; reset_subject_state(sid)
    update_subject_state(sid,'quero comprar um Corolla')
    update_subject_state(sid,'bom dia')
    assert get_subject_state(sid)['subject']=='corolla'
