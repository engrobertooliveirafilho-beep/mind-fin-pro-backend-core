from app.mind.p5_5s_source_expansion_autopilot import run_p55s_healthcheck
from app.mind.p5_5s_source_expansion_autopilot.autopilot import EXPANSION_TEMPLATES, SourceExpansionAutopilot

def test_p55s_healthcheck():
    assert run_p55s_healthcheck()["status"]=="P5.5S_READY"

def test_templates():
    assert len(EXPANSION_TEMPLATES) >= 6
    assert any(x[0]=="PEDIGREE_SEARCH" for x in EXPANSION_TEMPLATES)

def test_build_source_without_remote():
    ap=SourceExpansionAutopilot(url="https://example.supabase.co", key="fake")
    src=ap.build_source({"id":"1","official_name":"Bushwacker"}, "VIDEO_SEARCH", "Bushwacker PBR video")
    assert src["evidence_hash"]
    assert src["source_url"].startswith("https://www.google.com/search")
