from app.modules.usde_core.usde_core import USDECore
from app.main import app

def test_usde_core_smoke_backend():
    events = [
        {"id": 1, "values": [1,2,3]},
        {"id": 2, "values": [2,3,4]},
        {"id": 3, "values": [3,4,5]},
        {"id": 4, "values": [1,4,5]},
        {"id": 5, "values": [1,2,5]},
    ]
    result = USDECore().run(events, "tmp_usde_backend_test")
    assert result["decision"] in {"APROVADA_COM_EVIDENCIA", "INCONCLUSIVA", "HIPOTESE_REJEITADA"}

def test_usde_routes_registered():
    paths = [r.path for r in app.routes]
    assert "/usde/status" in paths
    assert "/usde/run" in paths
