from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, time, hashlib

from app.modules.usde_core.ingestors import load_events
from app.modules.usde_core.usde_core import USDECore
from app.modules.usde_core.evidence_engine import EvidenceEngine
from app.modules.usde_core.ledger import HypothesisLedger

@dataclass
class ScientificHypothesis:
    hypothesis_id: str
    statement: str
    dataset_ref: str
    params: dict

@dataclass
class ScientificExperiment:
    experiment_id: str
    hypothesis: ScientificHypothesis
    status: str
    created_at: float

@dataclass
class ScientificResult:
    experiment_id: str
    decision: dict
    evidence: dict
    artifacts_dir: str
    ledger_hash: str

class ScientificPipeline:
    def __init__(self, root: str = "_evidence/P4.46X_USDE_CORE/scientific_pipeline"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _id(self, payload: dict) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def create_hypothesis(self, statement: str, dataset_ref: str, params: dict | None = None) -> ScientificHypothesis:
        payload = {
            "statement": statement,
            "dataset_ref": dataset_ref,
            "params": params or {}
        }
        return ScientificHypothesis(
            hypothesis_id=self._id(payload),
            statement=statement,
            dataset_ref=dataset_ref,
            params=params or {}
        )

    def run(self, statement: str, dataset_ref: str, params: dict | None = None) -> dict:
        params = params or {}
        hypothesis = self.create_hypothesis(statement, dataset_ref, params)
        experiment_id = self._id({"hypothesis_id": hypothesis.hypothesis_id, "ts": time.time()})

        experiment = ScientificExperiment(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            status="RUNNING",
            created_at=time.time()
        )

        outdir = self.root / experiment_id
        outdir.mkdir(parents=True, exist_ok=True)

        events = load_events(dataset_ref)
        decision = USDECore(seed=params.get("seed", 42)).run(events, str(outdir / "artifacts"))

        evidence = EvidenceEngine().score(
            decision,
            metadata={
                "sample_size": len(events),
                "seed": params.get("seed", 42),
                "baseline": params.get("baseline", 0.0)
            }
        )

        ledger_record = HypothesisLedger().append(
            hypothesis=statement,
            dataset_ref=dataset_ref,
            decision={
                "decision": decision,
                "evidence": evidence,
                "experiment_id": experiment_id
            },
            params=params
        )

        result = ScientificResult(
            experiment_id=experiment_id,
            decision=decision,
            evidence=evidence,
            artifacts_dir=str(outdir / "artifacts"),
            ledger_hash=ledger_record["hash"]
        )

        (outdir / "hypothesis.json").write_text(
            json.dumps(asdict(hypothesis), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        (outdir / "experiment.json").write_text(
            json.dumps(asdict(experiment), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        (outdir / "scientific_result.json").write_text(
            json.dumps(asdict(result), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return asdict(result)
