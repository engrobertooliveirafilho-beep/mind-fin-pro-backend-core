"""ET665.BR: external video and cron execution remains disabled."""
import ast
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ("p1621e_real_video_fetch_loop", "fetch_metadata", ("https://example.invalid",)),
    ("p1621f_transcript_download_strategy_extraction", "fetch_subtitles", ("https://example.invalid",)),
    ("p1622_autonomous_daily_research_cron", "run_module", ("app.placeholder",)),
]
MARKER = "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"

@pytest.mark.parametrize("folder,entry,args", CASES)
def test_external_process_module_fail_closed(folder, entry, args, tmp_path, monkeypatch):
    target = ROOT / "app" / folder / "engine.py"
    tree = ast.parse(target.read_text(encoding="utf-8"))
    assert not any(
        isinstance(n, ast.Import) and any(a.name == "subprocess" for a in n.names)
        for n in ast.walk(tree)
    )
    assert not any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "subprocess"
        for n in ast.walk(tree)
    )
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("et665_br_" + folder, target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match=MARKER):
        getattr(module, entry)(*args)
    with pytest.raises(RuntimeError, match=MARKER):
        module.run()
    assert not (tmp_path / "reports").exists()
