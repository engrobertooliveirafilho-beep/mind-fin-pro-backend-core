"""ET665.R180: fail-closed dataset path containment tests; no engine run or external I/O."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINES = (
    "app/p1516_multi_family_combo_backtest_executor/engine.py",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py",
)


def load_engine(relative, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "et665_r180_" + relative.replace("/", "_").replace(".", "_"),
        ROOT / relative,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DATA = tmp_path / "normalized"
    module.DATA.mkdir()
    return module


@pytest.mark.parametrize("relative", ENGINES)
def test_r180_accepts_only_paths_inside_normalized_root(relative, tmp_path):
    module = load_engine(relative, tmp_path)
    expected = module.DATA.resolve() / "nested" / "TEST_D1.csv"
    assert module.safe_dataset_path("nested/TEST_D1.csv") == expected


@pytest.mark.parametrize("relative", ENGINES)
@pytest.mark.parametrize(
    "candidate",
    (
        "../outside.csv",
        "nested/../../outside.csv",
        "/tmp/outside.csv",
        r"C:\\outside.csv",
        r"..\\outside.csv",
        "",
        None,
        42,
        "bad\x00name.csv",
    ),
)
def test_r180_rejects_absolute_traversal_and_malformed_names(relative, candidate, tmp_path):
    module = load_engine(relative, tmp_path)
    with pytest.raises(PermissionError):
        module.safe_dataset_path(candidate)


@pytest.mark.parametrize("relative", ENGINES)
def test_r180_rejects_symlink_escape(relative, tmp_path):
    module = load_engine(relative, tmp_path)
    outside = tmp_path / "outside.csv"
    outside.write_text("secret,data\n", encoding="utf-8")
    link = module.DATA / "linked.csv"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable in this offline Windows environment")
    with pytest.raises(PermissionError):
        module.safe_dataset_path("linked.csv")


@pytest.mark.parametrize("relative", ENGINES)
def test_r180_rejects_normalized_root_symlink(relative, tmp_path):
    module = load_engine(relative, tmp_path)
    root = module.DATA
    outside = tmp_path / "outside"
    outside.mkdir()
    root.rmdir()
    try:
        root.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlink creation is unavailable in this offline Windows environment")
    with pytest.raises(PermissionError):
        module.safe_dataset_path("dataset.csv")
