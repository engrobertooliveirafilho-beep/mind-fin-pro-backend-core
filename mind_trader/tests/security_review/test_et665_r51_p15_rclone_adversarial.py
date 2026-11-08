"""ET665.R51: offline adversarial tests of four P15 rclone wrappers."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINES = [
    "app/p1516_multi_family_combo_backtest_executor/engine.py",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py",
    "app/p153_p155_profit_market_data_pipeline/engine.py",
    "app/p156_p1510_real_edge_research_runtime/engine.py",
]


def load_engine(path):
    spec = importlib.util.spec_from_file_location("r51_" + path.replace("/", "_").replace(".", "_"), ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", ENGINES)
def test_r51_rejects_drive_destinations_and_non_copy_commands(path):
    module = load_engine(path)
    wrapper = getattr(module, "run_cmd", None) or getattr(module, "cmd")
    forbidden = [
        'rclone copy "/tmp/local" "gdrive:history"',
        'rclone sync "gdrive:history" "/tmp/local"',
        'rclone delete "gdrive:history" "/tmp/local"',
        'rclone copy "gdrive:history" "gdrive:other"',
        'rclone copy "gdrive:history" "/tmp/local" --backup-dir gdrive:other',
    ]
    with patch.object(module.subprocess, "run") as runner:
        for command in forbidden:
            with pytest.raises(PermissionError):
                wrapper(command)
        runner.assert_not_called()


@pytest.mark.parametrize("path", ENGINES)
def test_r51_local_read_only_copy_uses_argv_not_shell(path):
    module = load_engine(path)
    wrapper = getattr(module, "run_cmd", None) or getattr(module, "cmd")
    with patch.object(module.subprocess, "run") as runner:
        wrapper('rclone copy "gdrive:history" "/tmp/local" --progress')
        runner.assert_called_once()
        assert runner.call_args.kwargs["shell"] is False
        assert runner.call_args.kwargs["check"] is True
