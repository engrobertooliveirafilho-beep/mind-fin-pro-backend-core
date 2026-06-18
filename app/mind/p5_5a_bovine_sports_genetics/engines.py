from .core import P55AOrchestrator, BullIdentity, Evidence, BiomechanicsScore

class BullGlobalResearchEngine:
    def normalize_public_record(self, record: dict) -> dict:
        identity = BullIdentity(**{k:v for k,v in record.items() if k in BullIdentity.__dataclass_fields__})
        return {**record, "identity_key": identity.identity_key()}

class BullIdentityResolutionEngine:
    def resolve(self, candidates: list[dict]) -> dict:
        groups = {}
        for c in candidates:
            key = BullIdentity(c.get("official_name",""), c.get("aliases",[]), c.get("registry_number")).identity_key()
            groups.setdefault(key, []).append(c)
        return {"groups": groups, "duplicate_groups": {k:v for k,v in groups.items() if len(v)>1}}

class BullMediaIngestionEngine:
    def register_media(self, media: dict) -> dict:
        required = ["url","platform","title"]
        return {**media, **P55AOrchestrator().audit_payload(media, required)}

class BullVideoBiomechanicsEngine:
    def score(self, metrics: dict) -> dict:
        return BiomechanicsScore(**{k:v for k,v in metrics.items() if k in BiomechanicsScore.__dataclass_fields__}).composite()

class BullDigitalJudgeEngine:
    def compare(self, official_score: float, mind_score: float) -> dict:
        err = abs(float(official_score)-float(mind_score))
        return {"official_score": official_score, "mind_score": mind_score, "absolute_error": err, "percentage_error": round((err/max(official_score,1))*100,4)}

class BullPedigreeGraphEngine:
    def edge(self, parent_id: str, child_id: str, relation: str) -> dict:
        return {"parent_id": parent_id, "child_id": child_id, "relation": relation, "audit_status": "provisional"}

class BullGeneticInfluenceEngine:
    def influence_score(self, offspring_count=0, champion_offspring=0, avg_score=0, market_value=0) -> float:
        return round(min(100, offspring_count*0.5 + champion_offspring*6 + avg_score*0.4 + market_value/100000),4)

class BullMarketValuationEngine:
    def valuation_score(self, sport=0, pedigree=0, reproduction=0, market=0, rarity=0, media=0) -> float:
        return round(min(100, sport*.25 + pedigree*.2 + reproduction*.2 + market*.2 + rarity*.1 + media*.05),4)

class BullReproductionIntelligenceEngine:
    def cross_score(self, sire_score=0, dam_score=0, inbreeding_risk=0) -> float:
        return round(max(0, min(100, sire_score*.45 + dam_score*.45 - inbreeding_risk*.25)),4)

class BullGlobalComparatorEngine:
    def country_score(self, metrics: dict) -> float:
        vals = [float(v) for v in metrics.values() if isinstance(v,(int,float))]
        return round(sum(vals)/len(vals),4) if vals else 0.0

class BullPredictionEngine:
    def champion_probability(self, biomechanics=0, pedigree=0, reproduction=0, market_signal=0) -> float:
        return round(max(0, min(1, (biomechanics*.35 + pedigree*.3 + reproduction*.25 + market_signal*.1)/100)),4)

class BullQualityAuditEngine:
    def audit(self, payload: dict, required: list[str]) -> dict:
        return P55AOrchestrator().audit_payload(payload, required)

class BullExecutiveDecisionEngine:
    def recommend(self, question_type: str, candidates: list[dict]) -> dict:
        ranked = sorted(candidates, key=lambda x: x.get("final_score",0), reverse=True)
        best = ranked[0] if ranked else None
        return {"question_type": question_type, "recommendation": best, "alternatives": ranked[1:5], "confidence": best.get("confidence_score",0) if best else 0}
