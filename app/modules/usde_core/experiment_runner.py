from __future__ import annotations
from pathlib import Path
from app.modules.usde_core.usde_core import USDECore
from app.modules.usde_core.ingestors import load_events
from app.modules.usde_core.ledger import HypothesisLedger

class ExperimentRunner:
    def __init__(self, outroot: str = "_evidence/P4.46X_USDE_CORE/experiments"):
        self.outroot = Path(outroot)
        self.outroot.mkdir(parents=True, exist_ok=True)

    def run_file(self, path: str, hypothesis: str, params: dict | None = None) -> dict:
        dataset = Path(path)
        if not dataset.exists():
            raise FileNotFoundError(path)

        exp_slug = dataset.stem.replace(" ", "_")
        outdir = self.outroot / exp_slug
        events = load_events(str(dataset))
        decision = USDECore(seed=(params or {}).get("seed", 42)).run(events, str(outdir))

        record = HypothesisLedger().append(
            hypothesis=hypothesis,
            dataset_ref=str(dataset),
            decision=decision,
            params=params or {}
        )

        return {
            "experiment": exp_slug,
            "events": len(events),
            "outdir": str(outdir),
            "decision": decision,
            "ledger_hash": record["hash"]
        }
