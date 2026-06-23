from app.integrations.runpod_client import RunPodClient

def test_runpod_health_contract(monkeypatch):
    assert hasattr(RunPodClient, "health")
    assert hasattr(RunPodClient, "generate_image")
    assert hasattr(RunPodClient, "transcribe_audio")
