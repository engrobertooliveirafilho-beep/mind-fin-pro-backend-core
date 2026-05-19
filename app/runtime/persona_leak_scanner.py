from pathlib import Path
import json, re
BAD=[
"NEURA, sua tutora cognitiva",
"tutora cognitiva",
"acompanhar o contexto da conversa",
"como posso te ajudar hoje",
"Eu sou a NEURA",
"camada conversacional do MIND"
]
def scan(root="app"):
    rows=[]
    for p in Path(root).rglob("*.py"):
        txt=p.read_text(encoding="utf-8",errors="ignore")
        for i,line in enumerate(txt.splitlines(),1):
            for b in BAD:
                if b.lower() in line.lower():
                    rows.append({"file":str(p),"line":i,"pattern":b,"text":line.strip()[:300]})
    return rows
if __name__=="__main__":
    rows=scan()
    Path("_evidence").mkdir(exist_ok=True)
    Path("_evidence/PERSONA_LEAK_SCAN.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"hits":len(rows),"rows":rows[:20]},ensure_ascii=False,indent=2))

