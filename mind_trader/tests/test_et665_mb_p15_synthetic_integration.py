"""ET665.MB integrated synthetic P15 smoke tests; no network, Drive, MT5 or broker."""
import csv
import importlib.util
import json
import math
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("app/p1516_multi_family_combo_backtest_executor/engine.py", "p1516", "mind_p1516_combo_runtime"),
    ("app/p1525b_cloud_dataset_reconstruction_fix/engine.py", "p1525b", "mind_p1525b_reconstruction"),
    ("app/p153_p155_profit_market_data_pipeline/engine.py", "p153_p155", "mind_p15_market_data_runtime"),
    ("app/p156_p1510_real_edge_research_runtime/engine.py", "p156_p1510", "mind_p15_edge_runtime"),
]

def normalized(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "timeframe", "date", "open", "high", "low", "close", "volume", "quantity"])
        for i in range(180):
            price = round(100 + i * 0.02 + math.sin(i / 5) * 8, 4)
            writer.writerow(["TEST", "D1", str(i), price, price + 1, price - 1, price, 1000 + i, 1])

def raw(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="latin1") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Data", "Abertura", "Máximo", "Mínimo", "Fechamento", "Volume", "Quantidade"])
        for i in range(180):
            price = f"{100 + i / 10:.2f}".replace(".", ",")
            writer.writerow([str(i), price, price, price, price, "100", "1"])

@pytest.mark.parametrize("path,engine_id,scratch", CASES)
def test_full_engine_offline_with_synthetic_dataset(path, engine_id, scratch, tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("et665_mb_" + engine_id, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TMP = tmp_path / scratch
    if hasattr(module, "DATA"):
        module.DATA = module.TMP / "normalized"
    if hasattr(module, "RAW"):
        module.RAW = module.TMP / "raw"
        module.NORM = module.TMP / "normalized"

    def fake_read_only_copy(command):
        assert command.startswith('rclone copy "gdrive:'), "Only read-only source allowed"
        assert "--progress" in command
        if engine_id == "p153_p155":
            raw(module.RAW / "TEST_Diario.csv")
        else:
            normalized(module.DATA / "TEST_D1_normalized.csv")
        return None

    if hasattr(module, "cmd"):
        monkeypatch.setattr(module, "cmd", fake_read_only_copy)
    else:
        monkeypatch.setattr(module, "run_cmd", fake_read_only_copy)
    if engine_id == "p1516":
        module.QUEUE = tmp_path / "queue.json"
        module.QUEUE.write_text(json.dumps([
            {"asset": "TEST", "timeframe": "D1", "dataset": "TEST_D1_normalized.csv", "pattern": "rsi_reversion"}
        ]), encoding="utf-8")
    if engine_id == "p1525b":
        module.EDGES = tmp_path / "edges.json"
        module.EDGES.write_text(json.dumps([
            {"dataset": "TEST_D1_normalized.csv", "symbol": "TEST", "timeframe": "D1",
             "strategy": "sma_cross", "fast": 5, "slow": 21}
        ]), encoding="utf-8")

    result = module.run()
    assert result["REAL_ORDERS"] == "FORBIDDEN"
    assert result["LIVE"] == "FORBIDDEN"
    assert result["REAL_BROKER"] == "DISABLED"
    staged = list((tmp_path / "et665_cm6_exports").glob(engine_id + "_*/manifest.sha256.json"))
    assert len(staged) == 1, "Exactly one local evidence package required"
    manifest = json.loads(staged[0].read_text(encoding="utf-8"))
    assert manifest["status"] == "STAGED_FOR_REVIEW_NOT_PUBLISHED"
    assert manifest["files"], "Report evidence must not be empty"
    assert not module.TMP.exists(), "Scratch cleanup required"
