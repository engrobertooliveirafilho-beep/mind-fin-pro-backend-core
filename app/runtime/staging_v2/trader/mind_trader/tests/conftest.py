from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# app.*
if "app" not in sys.modules:
    app_mod = types.ModuleType("app")
    app_mod.__path__ = [str(APP)]
    sys.modules["app"] = app_mod

# mind_trader.app.*
if "mind_trader" not in sys.modules:
    mt = types.ModuleType("mind_trader")
    mt.__path__ = [str(ROOT)]
    sys.modules["mind_trader"] = mt

sys.modules["mind_trader.app"] = sys.modules["app"]
