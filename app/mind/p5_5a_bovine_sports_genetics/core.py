from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib, json, re

AGENTS = [
    "Bull Research Agent","Video Analysis Agent","Pedigree Agent","Judge Agent",
    "Auction Agent","Genetics Agent","Market Agent","Lineage Agent","DNA Agent",
    "Reproduction Agent","Validation Agent","Quality Agent","Executive Decision Agent"
]

MODULES = [
    "bull_global_research_engine","bull_identity_resolution_engine","bull_media_ingestion_engine",
    "bull_video_biomechanics_engine","bull_digital_judge_engine","bull_pedigree_graph_engine",
    "bull_genetic_influence_engine","bull_market_valuation_engine","bull_reproduction_intelligence_engine",
    "bull_global_comparator_engine","bull_prediction_engine","bull_quality_audit_engine",
    "bull_executive_decision_engine"
]

SOURCE_TYPES = [
    "ABBI","PBR","PBR_BRASIL","PRCA","NFR","CBR","AUCTION","GENETIC_CATALOG",
    "YOUTUBE","FACEBOOK","INSTAGRAM","TIKTOK","BREEDER_SITE","COMPANY_SITE",
    "ARTICLE","JOURNAL","MAGAZINE","PODCAST","HISTORIC_VIDEO","ACADEMIC","VETERINARY","OTHER"
]

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def evidence_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip().lower())

def confidence_band(score: float) -> str:
    if score < 40: return "rejected"
    if score < 60: return "weak"
    if score < 75: return "provisional"
    if score < 90: return "reliable"
    return "highly_reliable"

@dataclass
class Evidence:
    source_url: str
    source_type: str = "OTHER"
    captured_at: str = field(default_factory=utcnow_iso)
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0

    def to_record(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data["evidence_hash"] = evidence_hash(data)
        data["validation_status"] = confidence_band(self.confidence_score)
        return data

@dataclass
class BullIdentity:
    official_name: str
    aliases: List[str] = field(default_factory=list)
    registry_number: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    breeder: Optional[str] = None
    owner: Optional[str] = None
    company: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    life_status: str = "unknown"

    def identity_key(self) -> str:
        seed = "|".join([normalize_name(self.official_name), str(self.registry_number or ""), str(self.birth_year or "")])
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

@dataclass
class BiomechanicsScore:
    jump_height: Optional[float] = None
    jump_length: Optional[float] = None
    horizontal_velocity: Optional[float] = None
    vertical_velocity: Optional[float] = None
    acceleration: Optional[float] = None
    initial_explosion: Optional[float] = None
    air_time: Optional[float] = None
    kick_frequency: Optional[float] = None
    kick_amplitude: Optional[float] = None
    direction_changes: Optional[int] = None
    angular_velocity: Optional[float] = None
    estimated_torque: Optional[float] = None
    estimated_kinetic_energy: Optional[float] = None
    estimated_power: Optional[float] = None
    unpredictability: Optional[float] = None
    sporting_aggressiveness: Optional[float] = None
    consistency: Optional[float] = None
    difficulty: Optional[float] = None

    def composite(self) -> Dict[str, float]:
        vals = [v for v in self.__dict__.values() if isinstance(v, (int,float))]
        base = sum(vals) / len(vals) if vals else 0.0
        return {
            "biomechanics_score": round(min(100, base), 4),
            "buckoff_pressure_score": round(min(100, ((self.initial_explosion or 0)+(self.unpredictability or 0)+(self.difficulty or 0))/3), 4),
            "explosiveness_score": round(min(100, self.initial_explosion or 0), 4),
            "spin_score": round(min(100, self.angular_velocity or 0), 4),
            "kick_score": round(min(100, ((self.kick_frequency or 0)+(self.kick_amplitude or 0))/2), 4),
            "difficulty_score": round(min(100, self.difficulty or 0), 4),
            "consistency_score": round(min(100, self.consistency or 0), 4),
        }

class P55AOrchestrator:
    mission = "P5.5A_GLOBAL_BOVINE_SPORTS_GENETICS_INTELLIGENCE_SYSTEM"

    def manifest(self) -> Dict[str, Any]:
        return {
            "mission": self.mission,
            "modules": MODULES,
            "agents": AGENTS,
            "source_types": SOURCE_TYPES,
            "principle": "No fact enters as truth without evidence, confidence, source and audit trail.",
            "created_at": utcnow_iso()
        }

    def audit_payload(self, payload: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        missing = [k for k in required if payload.get(k) in (None, "", [])]
        score = max(0, 100 - len(missing) * 12)
        return {
            "confidence_score": score,
            "audit_status": confidence_band(score),
            "missing_fields": missing,
            "evidence_hash": evidence_hash(payload),
            "last_verified_at": utcnow_iso()
        }

    def executive_question_types(self) -> List[str]:
        return [
            "which_bull_to_buy","which_cow_to_buy","which_semen_to_buy","which_embryo_to_buy",
            "which_pregnancy_to_buy","which_lineage_to_follow","undervalued_genetics",
            "overvalued_genetics","best_champion_cross","hidden_value_animal",
            "saturated_genetics","emerging_maternal_family","best_country_genetics"
        ]
