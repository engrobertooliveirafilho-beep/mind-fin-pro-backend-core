from pathlib import Path
from app.modules.usde_core.scientific_pipeline import ScientificPipeline

def test_scientific_pipeline_run():
    p = Path("tmp_scientific_pipeline.txt")
    p.write_text("1 - 01,02,03\n2 - 02,03,04\n3 - 03,04,05\n4 - 01,04,05\n5 - 01,02,05\n", encoding="utf-8")

    result = ScientificPipeline("_evidence/P4.46X_USDE_CORE/test_pipeline").run(
        "Toda hipótese nasce falsa até sobreviver ao teste.",
        str(p),
        {"seed": 42, "baseline": 0.5}
    )

    assert "experiment_id" in result
    assert "decision" in result
    assert "evidence" in result
    assert "ledger_hash" in result
    assert result["evidence"]["verdict"] in {"STRONG_EVIDENCE", "WEAK_OR_INCONCLUSIVE"}
