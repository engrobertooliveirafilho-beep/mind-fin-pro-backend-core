"""ET665.R49 static regression: historical MT5 scripts cannot reach terminal."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "reports/P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE/p1804_real_mt5_history_download_probe.py",
    ROOT / "reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION/p1805_symbol_discovery_10y_normalization.py",
]


def test_r49_no_mt5_import_or_terminal_access():
    for path in FILES:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) and any(a.name == "MetaTrader5" for a in n.names) for n in ast.walk(tree)), str(path)
        assert not any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "mt5" for n in ast.walk(tree)), str(path)
        assert any(isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) and isinstance(n.exc.func, ast.Name) and n.exc.func.id == "PermissionError" for n in tree.body), str(path)
