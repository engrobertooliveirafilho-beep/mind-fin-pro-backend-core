from pathlib import Path
from app.modules.usde_core.ingestors import load_events

def test_txt_ingestor():
    p = Path("tmp_usde_ingestor.txt")
    p.write_text("1 - 01,02,03\n2 - 02,03,04\n", encoding="utf-8")
    events = load_events(str(p))
    assert events == [
        {"id": 1, "values": [1,2,3]},
        {"id": 2, "values": [2,3,4]},
    ]

def test_csv_ingestor():
    p = Path("tmp_usde_ingestor.csv")
    p.write_text("1,1,2,3\n2,2,3,4\n", encoding="utf-8")
    events = load_events(str(p))
    assert events[0]["id"] == 1
    assert events[0]["values"] == [1,2,3]
