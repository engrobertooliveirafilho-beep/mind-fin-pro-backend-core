"""ET665.R186: isolated regressions; never connects to MT5, network or brokers."""
import ast
import importlib.util
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"

def load_engine(folder):
    path = APP / folder / "engine.py"
    spec = importlib.util.spec_from_file_location("r186_" + folder, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_p138_rejects_before_creating_directory(tmp_path, monkeypatch):
    import pytest
    monkeypatch.chdir(tmp_path)
    mod = load_engine("p138_platform_connectors")
    with pytest.raises(PermissionError, match="ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"):
        mod.run()
    assert not (tmp_path / "reports").exists()
    assert not (tmp_path / "data").exists()

def test_p139_rejects_before_creating_directory(tmp_path, monkeypatch):
    import pytest
    monkeypatch.chdir(tmp_path)
    mod = load_engine("p139_mt5_historical_data_puller")
    with pytest.raises(PermissionError, match="ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"):
        mod.run()
    assert not (tmp_path / "reports").exists()

def test_p138_bridge_probes_are_read_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = load_engine("p138_platform_connectors")
    mod.profit_probe()
    mod.ftmo_probe()
    assert not (tmp_path / "data").exists()

def test_p1310_schema_is_not_provenance(tmp_path):
    mod = load_engine("p1310_mt5_normalized_dataset_certification")
    file = tmp_path / "MT5_FAKE.csv"
    file.write_text("time,open,high,low,close\n" + "2026-01-01,1,2,0,1\n" * 200, encoding="utf-8")
    result = mod.inspect_csv(file)
    assert result["schema_ok"] and result["schema_sample_sufficient"]
    assert result["certified"] is False
    assert result["provenance_verified"] is False
    assert result["chronology_verified"] is False
    assert result["canonical_manifest_reconciled"] is False
    assert result["source"] == "UNVERIFIED"

def test_p1515_rejects_existing_self_certification(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = load_engine("p1515_web_research_to_backtest_queue")
    path = tmp_path / mod.DATASETS
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([{"normalized":"WINFUT_M15_normalized.csv","dataset":{"certified":True}}]),encoding="utf-8")
    assert mod.certified_datasets() == []
    assert mod.build_queue() == []

def test_r186_prohibitions_in_all_changed_engines():
    for folder in ("p138_platform_connectors","p139_mt5_historical_data_puller","p1310_mt5_normalized_dataset_certification","p1515_web_research_to_backtest_queue"):
        tree = ast.parse((APP/folder/"engine.py").read_text(encoding="utf-8"))
        assert isinstance(tree, ast.Module)
        text = (APP/folder/"engine.py").read_text(encoding="utf-8")
        assert "order_send(" not in text
        assert '"REAL_ORDERS":"FORBIDDEN"' in text or folder in ("p138_platform_connectors","p139_mt5_historical_data_puller")
