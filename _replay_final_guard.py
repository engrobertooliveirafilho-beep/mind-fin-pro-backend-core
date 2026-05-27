import re, json
from fastapi.testclient import TestClient
import app.main as m

c=TestClient(m.app)
msgs=["Oi","Tudo bem?","Quem é você?","Como você está?","Por que está dando erro?","Aprofunde","E depois?","Procure o erro principal","Quanto é 4x6","deu errado de novo","consegue detalhar mais?","busque pelo problema","porque deu errado?","como resolvemos isso?","me explique melhor","quem é vc","vc está bem?"]
bad=re.compile(r"vamos seguir pelo ponto real|vamos aprofundar sem reiniciar|validar o próximo passo|me diga melhor|entendi\. continua|próximo passo",re.I)
out=[]
for msg in msgs:
    r=c.post("/webhook/whatsapp",data={"Body":msg,"From":"whatsapp:+559999999999"})
    clean=re.sub(r"<[^>]+>"," ",r.text).strip()
    out.append({"message":msg,"response":clean,"generic_detected":bool(bad.search(clean)),"response_len":len(clean)})
print(json.dumps(out,ensure_ascii=False,indent=2))
