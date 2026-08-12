from pathlib import Path
from app.modules.usde_core.experiment_runner import ExperimentRunner

def test_experiment_runner_file():
    p = Path("tmp_usde_runner.txt")
    p.write_text("1 - 01,02,03\n2 - 02,03,04\n3 - 03,04,05\n4 - 01,04,05\n", encoding="utf-8")
    r = ExperimentRunner("_evidence/P4.46X_USDE_CORE/test_experiments").run_file(
        str(p),
        "Teste smoke do runner",
        {"seed": 42}
    )
    assert r["events"] == 4
    assert "ledger_hash" in r
    assert r["decision"]["decision"] in {"APROVADA_COM_EVIDENCIA", "INCONCLUSIVA", "HIPOTESE_REJEITADA"}
