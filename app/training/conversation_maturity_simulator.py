from app.humanization.human_conversation_runtime import CASES,human_reply,score_response,has_identity_leak
import json, random, time
CATEGORIES=["smalltalk","amizade","opinião","followup","dúvida","crítica","sarcasmo leve","typo/noisy input","estudo","matemática","engenharia","emocional leve","cansaço","comparação","memória longitudinal","reflexão","disagreement","contextual recall","multimodal followup"]
def run(total=1200):
    rows=[]
    for i in range(total):
        prompt=CASES[i%len(CASES)]
        if i%17==0: prompt=prompt.replace("você","vc").replace("não","nao")
        response=human_reply(prompt,{"i":i})
        rows.append(score_response(prompt,response))
    leaks=sum(1 for r in rows if r["identity_leak"])
    avg=sum(r["score"] for r in rows)/len(rows)
    return {"total":len(rows),"categories":CATEGORIES,"identity_leaks":leaks,"identity_fallback_rate":round(leaks/len(rows),4),"humanization_score":round(avg,2),"passed":leaks/len(rows)<0.01 and avg>=95,"samples":rows[:50]}
if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2))
