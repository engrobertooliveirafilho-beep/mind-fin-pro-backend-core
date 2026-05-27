import re
from fastapi.testclient import TestClient
import app.main as m

orig=m._p412n_normalize_xml_response

def traced(message, xml):
    print("="*120)
    print("MESSAGE:",message)
    mm=re.search(r"<Message>(.*?)</Message>",xml,re.S)
    body_before=mm.group(1).strip() if mm else xml
    print("BODY_BEFORE:",body_before)

    out=orig(message,xml)

    mm2=re.search(r"<Message>(.*?)</Message>",out,re.S)
    body_after=mm2.group(1).strip() if mm2 else out
    print("BODY_AFTER:",body_after)
    print("XML_OUT:",out[:500])
    return out

m._p412n_normalize_xml_response=traced

c=TestClient(m.app)

for msg in [
"Quem é você?",
"Como você está?",
"Por que está dando erro?",
"Aprofunde",
"E depois?",
"Procure o erro principal"
]:
    print("\n\nMSG=",msg)
    r=c.post("/webhook/whatsapp",data={"Body":msg,"From":"whatsapp:+559999999999"})
    print("FINAL=",r.text)
