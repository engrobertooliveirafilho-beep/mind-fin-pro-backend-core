from app.mind.p5_5w_video_metadata_extractor import run_p55w_healthcheck
from app.mind.p5_5w_video_metadata_extractor.extractor import detect_video_signal, detect_animal

def test_p55w_healthcheck():
    assert run_p55w_healthcheck()["status"]=="P5.5W_READY"

def test_detect_video_signal():
    assert detect_video_signal({"title":"Bushwacker YouTube bull ride official score","source_url":"https://youtube.com","raw_payload":{}})

def test_detect_animal():
    assert detect_animal({"title":"Bushwacker PBR video","source_url":"https://x.com","raw_payload":{}})=="Bushwacker"
