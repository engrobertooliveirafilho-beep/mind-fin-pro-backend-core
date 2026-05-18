import re, time, requests
from app.medical_swarm.runtime import MedicalSwarmRuntime

class MedicalDebateEngine:

    def run_debate(self, topic):
        swarm = MedicalSwarmRuntime().simulate(topic)
        outputs = swarm.get("outputs", [])

        claims = []
        for o in outputs:
            txt = str(o.get("response", {}).get("response", o.get("error", "")))
            claims.append({
                "persona": o.get("persona"),
                "provider": o.get("provider"),
                "claim": txt[:1200],
                "risk_flags": self.detect_risks(txt),
                "evidence_score": self.evidence_score(txt),
                "hallucination_score": self.hallucination_score(txt)
            })

        consensus = self.consensus(claims)
        contradictions = self.detect_contradictions(claims)

        return {
            "status": "MEDICAL_DEBATE_ENGINE_OPERATIONAL",
            "topic": topic,
            "agents": len(outputs),
            "claims": claims,
            "consensus": consensus,
            "contradictions": contradictions,
            "safety_notice": "Conteúdo educacional. Não substitui médico, protocolo institucional ou emergência."
        }

    def detect_risks(self, txt):
        t = txt.lower()
        flags = []
        for k in ["dose", "dosagem", "antibiótico", "cirurgia", "intubação", "vasopressor", "choque", "óbito"]:
            if k in t:
                flags.append(k)
        return flags

    def evidence_score(self, txt):
        t = txt.lower()
        score = 0
        for k in ["guideline", "protocolo", "ensaio", "revisão", "meta-análise", "who", "nih", "pubmed", "surviving sepsis"]:
            if k in t:
                score += 1
        return min(score, 10)

    def hallucination_score(self, txt):
        t = txt.lower()
        score = 0
        if len(t) < 120: score += 3
        if "sempre" in t or "nunca" in t: score += 2
        if "garantido" in t: score += 3
        if not any(x in t for x in ["risco", "evidência", "protocolo", "avaliação", "diagnóstico"]): score += 2
        return min(score, 10)

    def consensus(self, claims):
        valid = [c for c in claims if c.get("claim")]
        avg_evidence = round(sum(c["evidence_score"] for c in valid)/max(len(valid),1),2)
        avg_hallucination = round(sum(c["hallucination_score"] for c in valid)/max(len(valid),1),2)
        return {
            "consensus_level": "HIGH" if avg_evidence >= 3 and avg_hallucination <= 4 else "MODERATE",
            "avg_evidence_score": avg_evidence,
            "avg_hallucination_score": avg_hallucination,
            "recommended_action": "usar como material educacional e validar contra guideline oficial atualizado"
        }

    def detect_contradictions(self, claims):
        joined = " ".join(c.get("claim","").lower() for c in claims)
        contradictions = []
        pairs = [("antibiótico imediato","não usar antibiótico"),("fluido","restrição hídrica"),("vasopressor","evitar vasopressor")]
        for a,b in pairs:
            if a in joined and b in joined:
                contradictions.append({"type":"POTENTIAL_CONTRADICTION","a":a,"b":b})
        return contradictions
