from app.eldora.core.feature_flags import is_enabled
from app.eldora.core.startup_manager import startup_report
from app.eldora.core.service_health_graph import service_health_graph

def test_eldora_feature_flags():
    assert is_enabled("eldora_runtime_enabled") is True

def test_eldora_startup_manager():
    assert startup_report()["status"] == "ok"

def test_eldora_service_health_graph():
    graph = service_health_graph()
    assert graph["status"] == "ok"
    assert graph["runtime"] == "eldora"
